nextflow.preview.dsl=2

//////////////////////////////////////////////////////
//  Process imports:
include {
    isParamNull;
} from './../processes/utils.nf' params(params)
include {
    SC__PREPARE_OBS_FILTER;
} from './../processes/h5adSubset' params(params)
include {
    SC__APPLY_OBS_FILTER;
} from './../processes/h5adSubset' params(params)

//////////////////////////////////////////////////////
//  Define the workflow 

workflow FILTER_BY_CELL_METADATA {

    take:
        // Expects (sampleId, h5ad) : Channel
        data
        // Describes: name of tool
        // Expects tool: (string || null)
        // Values
        // - tool != null:
        //   - The given tool is performing itself a cell-based annotation
        //   - params.sc[tool] should exist
        // - tool == null:
        //   - params.sc.cell_filter should exist
        tool

    main:
        def workflowParams = isParamNull(tool) ? params.sc.cell_filter : params.sc[tool].cell_filter
        Channel
            .from(workflowParams.filters)
            .set{ filters }
        SC__PREPARE_OBS_FILTER(
            data.combine(filters),
            isParamNull(tool) ? 'NULL' : tool
        )
        out = SC__APPLY_OBS_FILTER(
            SC__PREPARE_OBS_FILTER.out.groupTuple(),
            isParamNull(tool) ? 'NULL' : tool
        )

    emit:
        out

}
