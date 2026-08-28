#!/bin/bash
# Exports architecture diagram from Mermaid markdown to high-resolution image
echo "Exporting Mermaid architecture diagram to docs/architecture_diagram.png..."
if command -v mmdc &> /dev/null; then
    mmdc -i docs/architecture.mmd -o docs/architecture_diagram.png -t dark -b transparent
    echo "Export successful!"
else
    echo "mmdc (Mermaid CLI) not detected. Mermaid diagram is rendered directly in README.md and Web UI."
fi
