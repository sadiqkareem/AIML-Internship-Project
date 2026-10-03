"""Run every samples/*.txt file through the model and write samples/sample_outputs.md.

Usage:
    python generate_samples.py
    python generate_samples.py --model distilbart
"""
import argparse
import glob
import os
import sys

import summarizer
from readability import readability

HERE = os.path.dirname(os.path.abspath(__file__))


def generate_samples(target_models=None):
    if not target_models:
        target_models = ["distilbart", "t5-small"]

    out = ["# Sample Summarization Outputs\n"]
    out.append("Pre-generated sample outputs comparing model engines, lengths, and readability scores.\n")

    txt_files = sorted(glob.glob(os.path.join(HERE, "samples", "*.txt")))
    if not txt_files:
        print("No sample .txt files found in samples/")
        return

    for path in txt_files:
        text = open(path, encoding="utf-8").read()
        filename = os.path.basename(path)
        orig_stats = readability(text)

        out.append(f"## {filename}\n")
        out.append(
            f"**Original Article:** {orig_stats['words']} words, "
            f"Readability: {orig_stats['flesch_reading_ease']} ({orig_stats['label']}), "
            f"Reading Level: Grade {orig_stats['grade_level']}\n"
        )

        for model in target_models:
            if model not in summarizer.MODELS:
                continue
            model_info = summarizer.MODEL_METADATA.get(model, {})
            model_display = model_info.get("name", model.upper())

            for length in ("short", "medium"):
                try:
                    res = summarizer.summarize(text, model=model, length=length)
                    sum_stats = readability(res["summary"])
                    reduction = round(100 * (1 - sum_stats["words"] / max(1, orig_stats["words"])), 1)

                    out.append(f"### {model_display} ({model.upper()}) · {length.capitalize()} (~{reduction}% reduction)\n")
                    out.append(f"> {res['summary']}\n")
                    out.append(
                        f"- **Words:** {orig_stats['words']} → {sum_stats['words']} words\n"
                        f"- **Readability (Flesch):** {orig_stats['flesch_reading_ease']} → "
                        f"{sum_stats['flesch_reading_ease']} ({sum_stats['label']})\n"
                        f"- **Grade Level:** Grade {orig_stats['grade_level']} → Grade {sum_stats['grade_level']}\n"
                        f"- **Engine:** `{res['model']}`\n"
                    )
                except Exception as e:
                    out.append(f"### {model_display} · {length.capitalize()}\n")
                    out.append(f"*Could not generate with {model}: {e}*\n")

    output_path = os.path.join(HERE, "samples", "sample_outputs.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"[OK] Successfully wrote {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample summarization outputs")
    parser.add_argument("--model", type=str, help="Specific model to run (e.g. distilbart, t5-small, bart, t5)")
    args = parser.parse_args()

    models = [args.model] if args.model else ["distilbart", "t5-small"]
    generate_samples(models)
