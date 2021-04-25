from aws_cdk import (
        core,
        aws_codedeploy as codedeploy,
        aws_codepipeline as codepipeline,
        aws_codepipeline_actions as codepipeline_actions,
        aws_iam as iam,
        pipelines as pipelines,
    )

class AWSBootstrapKitLandingZonePipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, 
            email: str = None,
            forceEmailVerification: str = None,
            pipelineDeployableRegions: [] = None,
            nestedOU: str = None,
            rootHostedZoneDNSName: str = None,
            thirdPartyProviderDNSUsed: str = None,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        sourceArtifact = codepipeline.Artifact()
        cloudAssemblyArtifact = codepipeline.Artifact()
    
        pipeline = pipelines.CdkPipeline(self, 'Pipeline',
            pipeline_name = "AWSBootstrapKit-LandingZone",
            cloud_assembly_artifact = cloudAssemblyArtifact,
            source_action = codepipeline_actions.GitHubSourceAction(
                action_name = 'Github',
                output = sourceArtifact,
                branch = self.node.try_get_context('github_repo_branch'),
                oauth_token = core.SecretValue.secrets_manager('GITHUB_TOKEN'),
                owner = self.node.try_get_context('github_alias'),
                repo = self.node.try_get_context('github_repo_name'),
            ),
            synth_action = pipelines.SimpleSynthAction.standard_npm_synth(
                source_artifact = sourceArtifact,
                cloud_assembly_artifact = cloudAssemblyArtifact,
                subdirectory = "",
                install_command="npm install -g aws-cdk",
                build_command="pip install -r requirements.txt"
            ),
        )
    
        core.CfnOutput(self, "PipelineConsoleUrl",
            value = "https://%s.console.aws.amazon.com/codesuite/codepipeline/pipelines/%s/view?region=%s" % (self.region,pipeline.code_pipeline.pipeline_name, self.region))
        # p = pipeline.add_application_stage()
        prodStage = pipeline.add_application_stage(AWSBootstrapKitLandingZoneStage(self, 'Prod', email = "test"))
        
        # self.node.try_get_context("email"))
        INDEX_START_DEPLOY_STAGE = prodStage.next_sequential_run_order() -2
        
        prodStage.add_manual_approval_action(action_name='Validate', run_order=INDEX_START_DEPLOY_STAGE)
        
        deployableRegions = pipelineDeployableRegions if len(pipelineDeployableRegions) > 0 else self. region

        regionsInShellScriptArrayFormat = ' '.join(deployableRegions)

        prodStage.add_actions(pipelines.ShellScriptAction(
            action_name = 'CDKBootstrapAccounts',
            commands=["REGIONS_TO_BOOTSTRAP="+regionsInShellScriptArrayFormat,
                './lib/auto-bootstrap.sh "$REGIONS_TO_BOOTSTRAP"'],
            additional_artifacts=[sourceArtifact],
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=[
                        'sts:AssumeRole'
                    ],
                    resources=['arn:aws:iam::*:role/OrganizationAccountAccessRole'],
                ),
                iam.PolicyStatement(
                    actions= [
                        'organizations:ListAccounts',
                        'organizations:ListTagsForResource'
                    ],
                    resources= ['*'],
                )
            ])
        )
        
class AWSBootstrapKitLandingZoneStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, 
        email: str = None,
        forceEmailVerification: str = None,
        nestedOU: str = None,
        rootHostedZoneDNSName: str = None,
        thirdPartyProviderDNSUsed: str = None,
        **kwargs):
        super().__init__(scope, id, **kwargs)
        AwsOrganizationsStack(self, 'Prod',     
            email,
            forceEmailVerification,
            nestedOU,
            rootHostedZoneDNSName,
            thirdPartyProviderDNSUsed
        )

class AwsOrganizationsStack(core.Stack):
    # nestedOU should define here

    def __init__(self, scope: core.Construct, id: str, 
            email,
            forceEmailVerification,
            nestedOU,
            rootHostedZoneDNSName,
            thirdPartyProviderDNSUsed,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)