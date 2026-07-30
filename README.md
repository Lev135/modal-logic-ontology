# Modal Logic Ontology

**A knowledge base of modal logics and their properties, built with Souffle Datalog.**

This project collects known facts about modal logic systems and encodes them as Datalog rules. It can infer new relationships and visualize the resulting ontology as a graph.

> **⚠️ Early Development – Proceed with Caution**
>
> This project is in a **very raw, experimental state**:
>
> - **Incomplete knowledge base** – Currently contains only a small set of facts. Many relations are missing or may be incorrect.
> - **Buggy code** – Datalog rules and visualization scripts are under active development. Expect errors and incomplete outputs.
> - **Not production-ready** – This is a research prototype, not a stable tool.
>
> The codebase is **small and simple**, so curious explorers can still understand and experiment with it. Contributions are welcome in spirit, but please be patient with the rough edges.

## 🗺️ Visualization examples

All currently included logics:
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="out/all_logics/graph_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="out/all_logics/graph_light.png">
    <img alt="all_logics" width="80%">
  </picture>
</div>

Complexity for normal logics:
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="out/norm_complexity/graph_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="out/norm_complexity/graph_light.png">
    <img alt="norm_complexity" width="80%">
  </picture>
</div>

## 🤝 Contributing

> **⚠️ TODO – Contributing guidelines are not yet ready**

I appreciate your interest in contributing! However, the codebase is currently too raw and unstable to provide reliable contributing instructions. Installation steps, testing procedures, and code standards are still being figured out.

If you'd like to help despite this, here's what I can honestly say:

- The code is messy and likely buggy – you'll need to explore and experiment on your own.
- There are no formal tests or CI/CD pipelines yet.
- If you find something obvious to fix or improve, feel free to open an issue or pull request.

**For now**, the best way to contribute is to:
1. Explore the code and point out issues or missing facts.
2. Suggest improvements via GitHub Issues.
3. Be patient – this project is in early exploration phase.

## ✨ Features

- **Knowledge base** – Facts about modal logics encoded as Datalog predicates
- **Rule-based inference** – Automatically derives inclusion relations and properties
- **Visualization** – Generates graphs with property-based coloring
- **Extensible** – Easy to add new logics and facts

## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
