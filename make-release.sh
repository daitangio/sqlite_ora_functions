#!/bin/bash
if [ "$OS" == "Windows_NT" ] ; then
python_exec="python"
else
python_exec="python3"
fi
$python_exec liteplus.py :memory:  doc/doc_builder.sql >doc/function_documentation.txt