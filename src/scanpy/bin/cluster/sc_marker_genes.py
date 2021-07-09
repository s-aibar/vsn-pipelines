#!/usr/bin/env python3

import argparse
import os
import scanpy as sc
import numpy as np
import warnings
import textwrap

parser = argparse.ArgumentParser(description='')

parser.add_argument(
    "normalized_tranformed_data",
    type=argparse.FileType('r'),
    help='Input h5ad file containing the log normalised data.'
)

parser.add_argument(
    "clustered_data",
    type=argparse.FileType('r'),
    help='Input h5ad file containing clustering information.'
)

parser.add_argument(
    "output",
    type=argparse.FileType('w'),
    help='Output h5ad file.'
)

parser.add_argument(
    "-x", "--method",
    type=str,
    action="store",
    dest="method",
    default="wilcoxon",
    help="The default 'wilcoxon' uses Wilcoxon rank-sum, ‘t-test_overestim_var’ overestimates variance of each group,"
         " 't-test' uses t-test,  'logreg' uses logistic regression. See [Ntranos18], here and here, for why this is"
         " meaningful."
)
parser.add_argument(
    "-g", "--groupby",
    type=str,
    action="store",
    dest="groupby",
    default="louvain",
    help="The key of the observations grouping to consider."
)
parser.add_argument(
    "-n", "--ngenes",
    type=int,
    action="store",
    dest="ngenes",
    default=None,
    help="The number of genes that appear in the returned tables. Defaults to all genes."
)

args = parser.parse_args()

# Define the arguments properly
FILE_PATH_IN = args.clustered_data
FILE_PATH_OUT_BASENAME = os.path.splitext(args.output.name)[0]

# I/O
# Expects h5ad file
try:
    normalized_tranformed_data = sc.read_h5ad(filename=args.normalized_tranformed_data.name)
    adata = sc.read_h5ad(filename=FILE_PATH_IN.name)
except IOError:
    raise Exception("VSN ERROR: Can only handle .h5ad files.")

# if 'raw' not in dir(adata):
#     warnings.warn(
#         "There is no raw attribute in your anndata object. Differential analysis will be performed on the main (possibly normalised) matrix."
#     )

# sc.tl.rank_genes_groups expects log normalized data (source: https://github.com/theislab/scanpy/issues/517)
# .raw slot is updated by the AnnData generated by normalize_transform step
print("The sc.tl.rank_genes_groups function expects log normalized data. Updating .raw slot by the .X slot from the AnnData generated by the normalize_transform step...")
adata.raw = normalized_tranformed_data

if args.ngenes == 0:
    try:
        ngenes = adata.raw.shape[1]
    except AttributeError:
        ngenes = adata.shape[1]
        warnings.warn(
            "There is no raw attribute in your anndata object. Using the shape of the main matrix as the number of genes to report."
        )

print("Checking for singlets...")
num_cell_by_clusters = adata.obs[args.groupby].value_counts()
num_singlet_clusters = np.sum(num_cell_by_clusters == 1)
if num_singlet_clusters > 0:
    raise Exception(
        textwrap.fill(
            textwrap.dedent(
                f"""
                Abort.
                There were {num_singlet_clusters} singlet clusters detected in the clustering ({args.groupby}, resolution {adata.uns[args.groupby]['params']['resolution']}).
                Avoid this resolution or higher ones using {args.groupby} for this dataset or consider using the Leiden algorithm instead.
                """
            )
        )
    )

print("No singlet clusters detected. Proceed...")

print(f"Ranking genes for characterizing groups (aka sc.tl.rank_genes_groups) using {args.method} method...")
sc.tl.rank_genes_groups(
    adata,
    use_raw=True,  # Default is True but make this clear here
    groupby=args.groupby,
    method=args.method,
    n_genes=ngenes
)

print("Saving AnnData to h5ad file...")
warnings.warn(
    f"The {FILE_PATH_OUT_BASENAME}.h5ad file contains the AnnData with the log normalized data in its .raw slot"
)
adata.write_h5ad("{}.h5ad".format(FILE_PATH_OUT_BASENAME))
