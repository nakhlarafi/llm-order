#!/bin/bash

# Set the project name
project="Time"
technique="perfect_callgraph"
buckets="50"

# Loop through the versions and checkout the buggy version of the project
for version in {1..27}
do
    echo "Running test for ${project} version ${version} with ${technique} technique"
    # python order_test.py ${project} ${version} ${technique}
    # python order_test_split_chat.py ${project} ${version} ${technique} ${buckets}
    python order_test_split.py ${project} ${version} ${technique} ${buckets}
    # python order_test_split.py ${project} ${version} ${technique}
    # python order_test_split_chat_summarize.py ${project} ${version} ${technique} ${buckets}
    # python gen_reasonings_incorrect.py ${project} ${version} ${technique}
done