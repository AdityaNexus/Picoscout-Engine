# graph_mermaid.py
from pathlib import Path

from src.graph import build_graph


def main() -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    graph = build_graph().get_graph()

    mermaid = graph.draw_mermaid()
    (output_dir / "graph.mmd").write_text(mermaid, encoding="utf-8")

    graph.draw_mermaid_png(output_file_path=str(output_dir / "graph.png"))

    print(f"Mermaid source: {output_dir / 'graph.mmd'}")
    print(f"Graph image:    {output_dir / 'graph.png'}")


if __name__ == "__main__":
    main()