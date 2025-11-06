from pyomo.environ import BuildAction

def define_hydrogen_shared_expressions(model):
    def prepPipelineLength_rule(model):
        for (n1,n2) in model.HydrogenBidirectionPipelines:
            if (n1,n2) in model.BidirectionalArc:
                model.PipelineLength[n1,n2] = model.transmissionLength[n1,n2]
            elif (n2,n1) in model.BidirectionalArc:
                model.PipelineLength[n1,n2] = model.transmissionLength[n2,n1]
            else:
                print('Error constructing hydrogen pipeline length for bidirectional pipeline ' + n1 + ' and ' + n2)
                exit()
    model.build_PipelineLength = BuildAction(rule=prepPipelineLength_rule)