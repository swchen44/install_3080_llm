#!/usr/bin/env python3
"""Convert one of the saved ComfyUI UI-format MiniMax H3 workflows to API format."""
import json
import sys
from pathlib import Path


def convert(source: Path, destination: Path, *, megapixels: float, duration: float, seed: int):
    workflow = json.loads(source.read_text())
    nodes = {str(node["id"]): node for node in workflow["nodes"]}
    result = {}
    for node_id, node in nodes.items():
        if node["type"] == "MarkdownNote":
            continue  # UI-only annotation nodes are not ComfyUI API nodes.
        api = {"class_type": node["type"], "inputs": {}}
        api["inputs"].update(node.get("widgets_values_named", {}))
        result[node_id] = api

    for link_id, origin_id, origin_slot, target_id, target_slot, _type in workflow["links"]:
        target = nodes[str(target_id)]
        if str(origin_id) not in result or str(target_id) not in result:
            continue
        input_name = target["inputs"][target_slot]["name"]
        result[str(target_id)]["inputs"][input_name] = [str(origin_id), origin_slot]

    # Keep the challenge prompt and six input images, but make a short 0.2 MP
    # canary. H3's legal frame grid turns 2 seconds into 56 frames.
    result["115"]["inputs"]["megapixels"] = megapixels
    result["132"]["inputs"]["value"] = duration
    result["129"]["inputs"]["noise_seed"] = seed
    result["92"]["inputs"]["filename_prefix"] = f"video/h3-attention-{source.stem}"

    destination.write_text(json.dumps({"prompt": result}, indent=2) + "\n")
    print(json.dumps({"source": str(source), "destination": str(destination),
                      "api_nodes": len(result), "megapixels": megapixels,
                      "duration_input": duration, "seed": seed}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit("usage: h3-ui-to-api.py SOURCE DESTINATION MEGAPIXELS DURATION SEED")
    convert(Path(sys.argv[1]), Path(sys.argv[2]), megapixels=float(sys.argv[3]),
            duration=float(sys.argv[4]), seed=int(sys.argv[5]))
