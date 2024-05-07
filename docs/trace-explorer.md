# Example Snowpark Trace Explorer

## Directions:

1. Follow the directions to [Create and View a Streamlit app by using Snowsight](https://docs.snowflake.com/en/developer-guide/streamlit/create-streamlit-ui).
2. For your app title enter "Example Snowpark Trace Explorer"
3. For your app location, choose the database and schema for your Event Table configuration
4. For your app warehouse, choose an appropriate value
5. Click "Create"

In the left pane, delete the sample code and replace it with the code below.

In the code below be sure to update these placeholder values to reflect your Event Table configuration:

- YOUR_EVENT_TABLE_DATABASE
- YOUR_EVENT_TABLE_SCHEMA
- YOUR_EVENT_TABLE_NAME

```python
import json
import streamlit as st

from snowflake.snowpark.context import get_active_session
from typing import List, Dict

# Write directly to the app
st.title("Example Snowpark Trace Explorer")

# Get the current credentials
session = get_active_session()

DATABASE = 'YOUR_EVENT_TABLE_DATABASE'
SCHEMA = 'YOUR_EVENT_TABLE_SCHEMA'
TABLE = 'YOUR_EVENT_TABLE_NAME'
FULLY_QUALIFIED_TABLE = ".".join([DATABASE, SCHEMA, TABLE])
MARKDOWN = ""

def event_to_dict(event_records):
    events = []
    for e in event_records:
        event_dict = e.as_dict(True)
        for k, v in event_dict.items():
            if k in ["TRACE", "RECORD", "RESOURCE_ATTRIBUTES"]:
                event_dict[k] = json.loads(v)
        events.append(event_dict)
    return events

def build_event_trees(events: List[Dict]):
    event_trees = []
    span_id_lookup = {}
    # Initialize lookup dict with each span_id as key
    for e in events:
        span_id = e["TRACE"]["span_id"]
        span_id_lookup[span_id] = e
        span_id_lookup[span_id]["CHILDREN"] = []
    for e in events:
        if "parent_span_id" in e["RECORD"].keys():
            parent_span_id = e["RECORD"]["parent_span_id"]
            span_id_lookup[parent_span_id]["CHILDREN"].append(e)
        else:
            event_trees.append(e)
    return event_trees

def dfs(curr_node, level, count_label):
    global MARKDOWN
    if curr_node is None:
        return
    MARKDOWN += "  " * level
    MARKDOWN += f"{count_label}. Span ID [{curr_node['TRACE']['span_id']}](# \"TRACE: {str(curr_node['TRACE'])}, RECORD: {str(curr_node['RECORD'])}, RESOURCE_ATTRIBUTES: {str(curr_node['RESOURCE_ATTRIBUTES'])}\") (mouse over for more)\n"
    MARKDOWN += "  " * level
    MARKDOWN += f"- `{curr_node['DURATION_MS']} ms duration, started {curr_node['STARTED']}`\n"
    if 'snow.executable.name' in curr_node['RESOURCE_ATTRIBUTES'].keys():
        curr_name = curr_node['RESOURCE_ATTRIBUTES']['snow.executable.name']
    else:
        curr_name = "ANONYMOUS " + curr_node['RESOURCE_ATTRIBUTES']['snow.executable.type']
    MARKDOWN += "  " * level
    MARKDOWN += f"- `{curr_name}`\n"
    if len(curr_node["CHILDREN"]) > 0:
        MARKDOWN += "  " * level
        MARKDOWN += f"- Children:\n"
    count_label = 0
    for child in curr_node["CHILDREN"]:
        count_label += 1
        dfs(child, level + 1, count_label)

query_id = st.text_area(
    "Query ID to trace:",
    "01b3f580-0609-1bac-0001-dd30d1705f13",
)

st.write(f"Searching for trace ID associated with {query_id}...")

# 1. Get trace_id from query_id.
trace = session.sql(
    f"""
    select trace['trace_id'] as trace_id
    from {FULLY_QUALIFIED_TABLE}
    where 1=1
        and startswith(resource_attributes['snow.query.id'], '{query_id.lower()}')
        and record_type = 'SPAN'
    limit 1;"""
).collect()
if len(trace) > 0:
    trace_dict = trace[0].as_dict()
    trace_id = trace_dict["TRACE_ID"].replace('"', '')
    st.write(f"Found trace ID {trace_id}")

    # 2. Get all spans for the given trace_id
    events_in_trace = session.sql(
        f"""
        select
            start_timestamp as started,
            timestamp as ended,
            datediff(millisecond, start_timestamp, timestamp) as duration_ms,
            trace,
            record,
            resource_attributes
        from {FULLY_QUALIFIED_TABLE}
        where 1=1
            and trace['trace_id'] = '{trace_id}'
            and record_type = 'SPAN'
        order by duration_ms desc;"""
    ).collect()

    # 3. Build and display tree of events based on parent_span_id
    root_events = build_event_trees(event_to_dict(events_in_trace))
    st.write("Span trees:")
    for root_event in root_events:
        MARKDOWN = ""
        dfs(root_event, level=0, count_label=1)
        st.write(MARKDOWN)
else:
    st.write('No trace ID found')
```
