#!/usr/bin/env python3
"""Build paired local ComfyUI MiniMax H3 R2V workflows for lcz.me/topic/3045."""
import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OFFICIAL = ROOT / "docs/research/workflows/video_minimax_h3_r2v.official.json"
PROMPT_DIR = ROOT / "docs/research/prompts"
ASSET_DIR = ROOT / "docs/research/assets/minimax-h3-lcz3045"
COMFY = Path.home() / "Downloads/ai/tools/comfyui-linux/ComfyUI-102350eb949bca599e450a904f0562ad3f551279"
INPUT_DIR = COMFY / "input/lcz3045"
OUT_DIR = ROOT / "docs/research/workflows"

IMAGES = [
    "jianxin-1.jpeg", "jianxin-2.jpeg", "jianxin-3.jpeg",
    "zhizhixiong-1.jpeg", "zhizhixiong-2.jpeg", "zhizhixiong-3.jpeg",
]

INPUT_DIR.mkdir(parents=True, exist_ok=True)
for filename in IMAGES:
    shutil.copy2(ASSET_DIR / filename, INPUT_DIR / filename)

base = json.loads(OFFICIAL.read_text())
by_id = {node["id"]: node for node in base["nodes"]}
reference = by_id[136]
# Add the four missing image ports using ComfyUI's autogrow schema order.
insert_at = next(i for i, port in enumerate(reference["inputs"]) if port["name"] == "ref_videos.ref_video_0")
new_ports = []
for index in range(3, 6):
    new_ports.append({
        "label": f"ref_image_{index}",
        "name": f"ref_images.ref_image_{index}",
        "shape": 7,
        "type": "IMAGE",
        "link": 290 + index,
    })
reference["inputs"][insert_at:insert_at] = new_ports
reference["inputs"][5]["link"] = 292
# Shift downstream connected input indexes (prompt, width, height, length).
for link in base["links"]:
    if link[3] == 136 and link[4] >= insert_at:
        link[4] += len(new_ports)

for node_id, image_index in zip(range(147, 151), range(2, 6)):
    source = copy.deepcopy(by_id[137])
    source["id"] = node_id
    source["pos"] = [-1050 + ((image_index - 2) % 2) * 350, 6350 + ((image_index - 2) // 2) * 390]
    filename = IMAGES[image_index]
    source["widgets_values"] = [f"lcz3045/{filename}", "image"]
    source["widgets_values_named"] = {"image": f"lcz3045/{filename}", "upload": "image"}
    link_id = 290 + image_index
    source["outputs"][0]["links"] = [link_id]
    base["nodes"].append(source)
    base["links"].append([link_id, node_id, 0, 136, 3 + image_index, "IMAGE"])

for node_id, filename in [(137, IMAGES[0]), (139, IMAGES[1])]:
    by_id[node_id]["widgets_values"] = [f"lcz3045/{filename}", "image"]
    by_id[node_id]["widgets_values_named"] = {"image": f"lcz3045/{filename}", "upload": "image"}

# Resolve template defaults that differ from the user's locally available baseline.
by_id[119]["widgets_values"] = ["minimax_h3_video_vae_fp16.safetensors"]
by_id[119]["widgets_values_named"]["vae_name"] = "minimax_h3_video_vae_fp16.safetensors"
by_id[119]["properties"]["models"] = [{
    "name": "minimax_h3_video_vae_fp16.safetensors",
    "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors",
    "directory": "vae",
}]
by_id[128]["widgets_values"][0] = "qwen3vl_32b_minimax_h3_int8_convrot.safetensors"
by_id[128]["widgets_values_named"]["clip_name"] = "qwen3vl_32b_minimax_h3_int8_convrot.safetensors"
by_id[128]["properties"]["models"] = [{
    "name": "qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
    "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
    "directory": "text_encoders",
}]
by_id[132]["widgets_values"] = [12.0]
by_id[132]["widgets_values_named"]["value"] = 12.0
by_id[115]["widgets_values"] = ["16:9 (Widescreen)", 0.984375, 32]
by_id[115]["widgets_values_named"].update({"aspect_ratio": "16:9 (Widescreen)", "megapixels": 0.984375, "multiple": 32})
by_id[136]["widgets_values"] = ["", 1344, 768, 294, "match"]
by_id[136]["widgets_values_named"].update({"width": 1344, "height": 768, "length": 294, "ref_image_size": "match"})
by_id[138]["widgets_values"] = [""]
by_id[138]["widgets_values_named"]["value"] = ""
by_id[129]["widgets_values"] = [261662374822964, "fixed"]
by_id[129]["widgets_values_named"].update({"noise_seed": 261662374822964, "control_after_generate": "fixed"})
by_id[92]["widgets_values"][0] = "video/lcz3045"
by_id[92]["widgets_values_named"]["filename_prefix"] = "video/lcz3045"
# Remove the optional Turbo-LoRA branch entirely. ComfyUI validates both sides
# of its switch and would reject this workflow when the optional LoRA is absent,
# even while the switch is false. Keep the native 20-step base model path.
remove_nodes = {141, 142, 144, 145, 146}
remove_links = {283, 285, 286, 288, 289, 290, 291}
for link in base["links"]:
    if link[0] == 287:  # Base model -> guider, bypassing the model switch.
        link[3:5] = [126, 0]
    elif link[0] == 284:  # Full-step count -> scheduler, bypassing the steps switch.
        link[3:5] = [124, 1]
base["nodes"] = [node for node in base["nodes"] if node["id"] not in remove_nodes]
base["links"] = [link for link in base["links"] if link[0] not in remove_links]
links_by_target = {(link[3], link[4]): link[0] for link in base["links"]}
links_by_source = {}
for link in base["links"]:
    links_by_source.setdefault((link[1], link[2]), []).append(link[0])
for node in base["nodes"]:
    for port in node.get("inputs", []):
        port["link"] = links_by_target.get((node["id"], node["inputs"].index(port)))
    for slot, port in enumerate(node.get("outputs", [])):
        port["links"] = links_by_source.get((node["id"], slot)) or None
base["last_node_id"] = 150
base["last_link_id"] = 295
base["extra"] = base.get("extra", {})

for style, filename in [("3d", "minimax-h3-lcz3045-3d.txt"), ("2d", "minimax-h3-lcz3045-2d.txt")]:
    workflow = copy.deepcopy(base)
    nodes = {node["id"]: node for node in workflow["nodes"]}
    prompt = (PROMPT_DIR / filename).read_text().strip()
    nodes[138]["widgets_values"] = [prompt]
    nodes[138]["widgets_values_named"]["value"] = prompt
    nodes[92]["widgets_values"][0] = f"video/lcz3045_{style}"
    nodes[92]["widgets_values_named"]["filename_prefix"] = f"video/lcz3045_{style}"
    target = OUT_DIR / f"minimax-h3-lcz3045-{style}.json"
    target.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n")

print(f"Created 3D and 2D workflows from {OFFICIAL}")
print(f"Copied {len(IMAGES)} references to {INPUT_DIR}")
