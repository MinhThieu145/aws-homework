from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
)


class CdkEc2AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # get key pair
        # In order to get key pair, you'll need the public key material. To get the public key material, please go to this link:https://serverfault.com/questions/334670/cannot-import-ec2-keypair-length-exceeds-maximum-via-aws-console-from-existing
        key_pair = ec2.CfnKeyPair(self, "Key Pair For Ec2 Homework",
                                    key_name="Key Pair For Ec2 Homework",
                                    public_key_material="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCfyki6vw5sDXpyAdHhWyMvK71N8HxypYYhEN4xhvMBBmq6jWSF4ZC2JCSlQHb6/X8fgTrl7aAdihm+eSvtvdL99jZr+Xi1K/j/s7k8JnO+p6RKbKL/eFUiosI1PxM3eLCAY0U7/tt4BFPGJ0WID+j8INmCs8UGzf3WWXt5lWliEVYQzciJSu2yccW3pl4JvYf5NcnWh/VusETWDdgUXW8Sr+Jg4UGkMKNMDKB4lhOKVbbBAsTKOiyBXUJl7DlrtI/864MWYGAzP81vrfZZMaUTPIQ+m4HWbeLOGwhNQAP1z1npkU+nF2I1ARjKPNmDo+4YmXYNHyh0Kzfosk6oBvbf")
        
                               

        # create a vpc for your ec2 instance

        # Note: for some reason it already has Internet Gateway for default. Maybe because of the subnet
        # they also have a route table with route to Internet Gateway already lol
        vpc = ec2.Vpc(self, "VPC For Ec2 Homework",
                        cidr="10.0.0.0/16", # chinh CIDR block cho vpc
                        max_azs=1, # ko thay setting cai nay trong console
                        
                        # create 1 cai subnet cho cai nay. Do Ec2 nay minh chi can public nen ko can private subnet
                        subnet_configuration=[
                            ec2.SubnetConfiguration(
                                name="Public Subnet Homework Ec2",
                                subnet_type=ec2.SubnetType.PUBLIC, # do cai nay la public nen nhieu cai setting da chinh san so voi console
                                cidr_mask=24, # cai cidr cho subnet nay. La 1 nua subnet cua vpc (vpc la /16)
                            )
                        ])
        
        # get the public subnet
        public_subnet = vpc.public_subnets[0] # vi minh chi tao 1 subnet nen chi co 1 phan tu trong list

        # get the route table of the public subnet


        # # create a route table for the public subnet
        # route_table = ec2.CfnRouteTable(
        #     self, "Route Table For Public Subnet",
        #     vpc_id=vpc.vpc_id,
        # )

        # # Create the route with the public subnet to access the internet
        # ec2.CfnRoute(
        #     self, "Route For Public Subnet",
        #     route_table_id=route_table.ref,
        #     destination_cidr_block="0.0.0.0/0",
        #     gateway_id=vpc.internet_gateway_id,
        # )

        # # associate the public subnet with the route table
        # ec2.CfnSubnetRouteTableAssociation(
        #     self, "Associate Public Subnet With Route Table",
        #     subnet_id=public_subnet.subnet_id,
        #     route_table_id=route_table.ref,
        # )



        # create security group for ec2 instance
        security_group = ec2.SecurityGroup(self, "Security Group For Ec2 Homework",
                                            vpc=vpc,
                                            allow_all_outbound=True,
                                            security_group_name="Security Group For Ec2 Homework",
                                            description="Security Group For Ec2 Homework",
                                            )
        
        # add inboud rule for security group. Allow SSH inbound traffic
        security_group.add_ingress_rule(peer=ec2.Peer.ipv4('131.247.226.141/32') # use only my IP address for port 22
                                        , connection=ec2.Port.tcp(22), description="Allow SSH inbound traffic")

        # allow HTTP inbound traffic
        security_group.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(80), description="Allow HTTP inbound traffic")

        # allow HTTPS inbound traffic
        security_group.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(443), description="Allow HTTPS inbound traffic")

        # add a custom TCP port inbound rule for 8501 port (because streamlit use this port)
        security_group.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(8501), description="Allow 8501 inbound traffic")

        # get a role
        ec2_role = iam.Role.from_role_arn(self, id="Ec2 Homework Role", role_arn="arn:aws:iam::238101178196:role/ec2-S3-InvokeLambda-WriteLog")


        # Now create ec2 instance
        # to look up image: https://stackoverflow.com/questions/67675888/how-to-look-up-an-ami-id-for-use-with-the-l1-cfninstance-construct
        ec2_instance = ec2.Instance(self, "Ec2 Homework",
                                    instance_name="Ec2 Homework",
                                    instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.T2,instance_size=ec2.InstanceSize.MICRO),
                                    machine_image=ec2.MachineImage.latest_amazon_linux2023(user_data=ec2.UserData.custom(
                                        """
                                            #!/bin/bash
                                            yum update -y
                                            yum install -y python3 python3-pip
                                            pip3 install streamlit pandas boto3

                                    """
                                    )),
                                    vpc=vpc,
                                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                    security_group=security_group,  
                                    key_name=key_pair.key_name,
                                    role=ec2_role,
                                    )
        
