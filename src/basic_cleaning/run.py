#!/usr/bin/env python
"""Download a W&B artifact, perform basic cleaning, and log the result."""

import argparse
import logging

import pandas as pd

import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact.
    logger.info(f"Download artifact {args.input_artifact}")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    logger.info("Drop price outliers")
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Cast `last_review` to datetime")
    df["last_review"] = pd.to_datetime(df["last_review"])

    idx = df["longitude"].between(-74.25, -73.50) & df["latitude"].between(40.5, 41.2)
    df = df[idx].copy()
    

    df.to_csv(args.output_artifact, index=False)

    logger.info(f"Upload artifact {args.output_artifact}")
    artifact = wandb.Artifact(
        args.output_artifact, type=args.output_type, description=args.output_description
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name of input artifact",
        required=True,
    )
    parser.add_argument(
        "--output_artifact",
        type=str,
        help="name of the output artifact",
        required=True,
    )
    parser.add_argument(
        "--output_type",
        type=str,
        help="type of output artifact",
        required=True,
    )
    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of output artifact",
        required=True,
    )
    parser.add_argument(
        "--min_price",
        type=float,
        help="minimum valid price",
        required=True,
    )
    parser.add_argument(
        "--max_price",
        type=float,
        help="maximum valid price",
        required=True,
    )

    args = parser.parse_args()
    go(args)
