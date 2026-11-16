#!/usr/bin/env python3
"""Verify prepared local MiniMax H3 workflows against lcz.me topic 3045 settings."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_DIR = ROOT / "docs/research/workflows"
PROMPT_DIR = ROOT / "docs/research/prompts"
EXPECTED_IMAGES = [
    "jianxin-1.jpeg", "jianxin-2.jpeg", "jianxin-3.jpeg",
    "zhizhixiong-1.jpeg", "zhizhixiong-2.jpeg", "zhizhixiong-3.jpeg",
]
EXPECTED_SEED = 261662374822964
EXPECTED_DIFFUSION = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
EXPECTED_ENCODER = "qwen3vl_32b_minimax_h3_int8_convrot.safetensors"
EXPECTED_VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
EXPECTED_AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"


def verify(style: str) -> dict:
    path = WORKFLOW_DIR / f"minimax-h3-lcz3045-{style}.json"
    workflow = json.loads(path.read_text())
    nodes = {node["id"]: node for node in workflow["nodes"]}
    selector = nodes[115]
    ratio = (16, 9)
    megapixels = selector["widgets_values"][1]
    multiple = selector["widgets_values"][2]
    scale = math.sqrt(megapixels * 1024 * 1024 / (ratio[0] * ratio[1]))
    resolved = [round(ratio[i] * scale / multiple) * multiple for i in (0, 1)]
    assert resolved == [1344, 768], f"Resolution selector gives {resolved}"
    assert selector["widgets_values"] == ["16:9 (Widescreen)", 0.984375, 32]

    ref_node = nodes[136]
    ref_ports = [port for port in ref_node["inputs"] if port["name"].startswith("ref_images.")]
    assert [port["name"] for port in ref_ports] == [f"ref_images.ref_image_{i}" for i in range(6)]
    assert all(port["link"] is not None for port in ref_ports), "Not all six reference inputs are connected"
    by_target_slot = {link[4]: nodes[link[1]] for link in workflow["links"]
                      if link[3] == 136 and link[5] == "IMAGE"}
    image_order = [by_target_slot[slot]["widgets_values"][0].split("/")[-1] for slot in range(3, 9)]
    assert image_order == EXPECTED_IMAGES, f"Reference order mismatch: {image_order}"

    assert ref_node["widgets_values"][1:4] == [1344, 768, 294]
    assert nodes[132]["widgets_values"] == [12.0]
    assert nodes[143]["widgets_values"][0] == 20
    assert nodes[129]["widgets_values"] == [EXPECTED_SEED, "fixed"]
    assert nodes[127]["widgets_values"][0] == EXPECTED_DIFFUSION
    assert nodes[128]["widgets_values"][0] == EXPECTED_ENCODER
    assert nodes[119]["widgets_values"][0] == EXPECTED_VIDEO_VAE
    assert nodes[120]["widgets_values"][0] == EXPECTED_AUDIO_VAE
    assert not ({141, 142, 144, 145, 146} & nodes.keys()), "Optional Turbo LoRA and switch nodes must be absent"
    assert any(link[1:5] == [127, 0, 126, 0] for link in workflow["links"]), "Base model must feed guider directly"
    assert any(link[1:5] == [143, 0, 124, 1] for link in workflow["links"]), "20-step value must feed scheduler directly"

    prompt_file = PROMPT_DIR / f"minimax-h3-lcz3045-{style}.txt"
    expected_prompt = prompt_file.read_text().strip()
    assert nodes[138]["widgets_values"] == [expected_prompt]
    expected_prefix = f"video/lcz3045_{style}"
    assert nodes[92]["widgets_values"][0] == expected_prefix

    return {"style": style, "workflow": str(path), "resolution": resolved,
            "reference_images": image_order, "frames": 294, "steps": 20,
            "seed": EXPECTED_SEED, "save_prefix": expected_prefix}


results = [verify(style) for style in ("3d", "2d")]
assert len(set(tuple(result["reference_images"]) for result in results)) == 1
workflows = [json.loads((WORKFLOW_DIR / f"minimax-h3-lcz3045-{style}.json").read_text()) for style in ("3d", "2d")]
nodes_by_style = [{node["id"]: node for node in workflow["nodes"]} for workflow in workflows]
for node_id in nodes_by_style[0]:
    if node_id not in (92, 138):
        assert nodes_by_style[0][node_id] == nodes_by_style[1][node_id], f"Unexpected workflow difference at node {node_id}"
prompt_3d = nodes_by_style[0][138]["widgets_values"][0]
prompt_2d = nodes_by_style[1][138]["widgets_values"][0]
assert prompt_3d.replace("3D CGI animation", "STYLE") == prompt_2d.replace("2D traditional anime", "STYLE"), "Prompt differs beyond the style phrase"
assert nodes_by_style[0][92]["widgets_values"][0].replace("_3d", "_STYLE") == nodes_by_style[1][92]["widgets_values"][0].replace("_2d", "_STYLE")
print(json.dumps({"status": "verified", "workflows": results}, indent=2))
