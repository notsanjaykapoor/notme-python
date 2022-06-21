import datadog

import stats_init  # noqa: F401
import dot_init  # noqa: F401
import services.database.session
import services.entities
import services.graph.query
import services.graph.session

CHECK_NAME = "notme.service_check"
CHECK_TAGS = ["check:graph-sync"]


def service_check() -> int:
    """check graph sync health"""

    with services.database.session.get() as db, services.graph.session.get() as neo:
        # database entity id count should match graph node count
        struct_db_count = services.entities.CountIds(db=db).call()
        db_count = struct_db_count.count

        struct_graph = services.graph.query.match_node_count()
        records = services.graph.query.execute(struct_graph.query, struct_graph.params, neo)

        graph_count = records[0]["count"]

        if db_count == graph_count:
            status = 0
            message = "ok"
        else:
            status = 2
            message = "graph sync invalid"

    datadog.statsd.service_check(
        check_name=CHECK_NAME,
        status=status,
        message=message,
        tags=CHECK_TAGS,
    )

    datadog.statsd.flush()

    return 0
