#!/usr/bin/env python
"""
download data from WB to perform cleaning export result as an artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()
    df = pd.read_csv(artifact_path)
    # Drop outliers
    logger.info("Drop outlier")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    logger.info("Convert String to Datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])
    logger.info("Saving Clean Sample DF")
    # fix a bug we saw with sample2.csv
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    df.to_csv("clean_sample.csv", index=False)

    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,)
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="a very basic data cleaning")


    parser.add_argument(
        "--input_artifact",
        type= str,## INSERT TYPE HERE: str, float or int,
        help= "path to input artifact",## INSERT DESCRIPTION HERE,
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type= str,## INSERT TYPE HERE: str, float or int,
        help= "path to output artifact",## INSERT DESCRIPTION HERE,
        required=True
    )

    parser.add_argument(
        "--output_type",
        type= str,## INSERT TYPE HERE: str, float or int,
        help= 'output is a csv file',## INSERT DESCRIPTION HERE,
        required=True
    )

    parser.add_argument(
        "--output_description",
        type= str,## INSERT TYPE HERE: str, float or int,
        help= "a clean dataframe saved to drive using the provided name",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type= float,## INSERT TYPE HERE: str, float or int,
        help= 'accepted min price',## INSERT DESCRIPTION HERE,
        required=True
    )

    parser.add_argument(
        "--max_price",
        type= float,## INSERT TYPE HERE: str, float or int,
        help= 'accepted max price',## INSERT DESCRIPTION HERE,
        required=True
    )


    args = parser.parse_args()

    go(args)
