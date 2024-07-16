There was an error in the input to the evaluation:

> {{error}}

Evaluation requires these inputs and bit widths:

{% for port in prog.inputs.values() -%}
* {{port.name}}: {{port.width}} bits
{% endfor %}
