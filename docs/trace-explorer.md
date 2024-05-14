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
EVENT_TABLE = 'YOUR_EVENT_TABLE_NAME'
FULLY_QUALIFIED_TABLE = ".".join([DATABASE, SCHEMA, EVENT_TABLE])
MARKDOWN = ""

def row_to_dict(span_rows):
    spans = []
    for row in span_rows:
        span_dict = row.as_dict(True)
        for k, v in span_dict.items():
            if k in ["TRACE", "RECORD", "RESOURCE_ATTRIBUTES"]:
                span_dict[k] = json.loads(v)
        spans.append(span_dict)
    return spans

def build_trace_trees(spans: List[Dict]):
    trace_trees = []
    span_id_lookup = {}
    # Initialize lookup dict with each span_id as key
    for span in spans:
        span_id = span["TRACE"]["span_id"]
        span_id_lookup[span_id] = span
        span_id_lookup[span_id]["CHILDREN"] = []
    for span in spans:
        if "parent_span_id" in span["RECORD"].keys():
            parent_span_id = span["RECORD"]["parent_span_id"]
            span_id_lookup[parent_span_id]["CHILDREN"].append(span)
        else:
            trace_trees.append(span)
    return trace_trees

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
        MARKDOWN += f"- Child span(s):\n"
    count_label = 0
    for child in curr_node["CHILDREN"]:
        count_label += 1
        dfs(child, level + 1, count_label)

query_id = st.text_area(
    "Query ID to trace:",
    "01b42d80-0002-65f7-0045-80070015d8d2",
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
    st.write(f"Found trace ID {trace_id}, now searching for all spans in the trace...")

    # 2. Get all spans for the given trace_id
    spans_in_trace = session.sql(
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

    # 3. Build and display trace trees based on parent_span_id
    root_spans = build_trace_trees(row_to_dict(spans_in_trace))
    st.write("Trace trees:")
    for root_span in root_spans:
        MARKDOWN = ""
        dfs(root_span, level=0, count_label=1)
        st.write(MARKDOWN)
else:
    st.write('No trace ID found')
```
