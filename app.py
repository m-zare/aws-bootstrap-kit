#!/usr/bin/env python3
import os

from aws_cdk import core

from aws_bootstrap_kit.aws_bootstrap_kit_stack import AWSBootstrapKitLandingZonePipelineStack
from aws_bootstrap_kit.aws_bootstrap_kit_stack import AWSBootstrapKitLandingZoneStage

app = core.App()

# nestedOU = [
#     {
#         name: 'SharedServices',
#         accounts: [
#             {
#                 name: 'CICD',
#                 type: AccountType.CICD
#             }
#         ]
#     },
#     {
#         name: 'SDLC',
#         accounts: [
#             {
#                 name: 'Dev',
#                 type: AccountType.PLAYGROUND
#             },
#             {
#                 name: 'Staging',
#                 type: AccountType.STAGE,
#                 stageName: 'staging',
#                 stageOrder: 1,
#                 hostedServices: ['ALL']
#             }
#         ]
#     },
#     {
#         name: 'Prod',
#         accounts: [
#             {
#                 name: 'Prod',
#                 type: AccountType.STAGE,
#                 stageName: 'prod',
#                 stageOrder: 2,
#                 hostedServices: ['ALL']
#             }
#         ]
#     }
# ]
email = app.node.try_get_context("email")
rootHostedZoneDNSName = app.node.try_get_context("domain_name")
thirdPartyProviderDNSUsed = app.node.try_get_context("third_party_provider_dns_used")
forceEmailVerification = app.node.try_get_context("force_email_verification")
pipelineDeployableRegions = app.node.try_get_context("pipeline_deployable_regions")
nestedOU = ''

AWSBootstrapKitLandingZoneStage(app, 'Prod',
    email,
    forceEmailVerification,
    nestedOU,
    rootHostedZoneDNSName,
    thirdPartyProviderDNSUsed
    )

AWSBootstrapKitLandingZonePipelineStack(app, "AWSBootstrapKit-LandingZone-PipelineStack",
    email,
    forceEmailVerification,
    pipelineDeployableRegions,
    nestedOU,
    rootHostedZoneDNSName,
    thirdPartyProviderDNSUsed
    )
app.synth()
