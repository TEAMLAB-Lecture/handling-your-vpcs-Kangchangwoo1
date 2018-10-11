import boto3

ec2 = boto3.resource('ec2', region_name="ap-southeast-1")

outfile = open('please input here','w')
key_pair = ec2.create_key_pair(KeyName='please input here'

KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)

key_name = raw_input("key_name을 입력해주세요.")
SubnetId = raw_input("SubnetId를 입력해주세요.")
VPC_id = raw_input("VPC_id를 입력해주세요.")
instance_type = raw_input("instance_type을 입력해주세요.")

nginx_AMI =	'ami-0cbad1ff1711f6e1d'
crontab_AMI = 'ami-036d344554b4b053a'

instances = ec2.create_instances(
    NetworkInterfaces=[{'SubnetId': SubnetId, 'DeviceIndex': 0, 'Groups': VPC_id}],
	ImageId=nginx_AMI,
	MinCount=1,
	MaxCount=4,
	KeyName=key_name,
	InstanceType=instance_type)

instances = ec2.create_instances(
    NetworkInterfaces=[{'SubnetId':SubnetId, 'DeviceIndex': 0, 'Groups': VPC_id}],
	ImageId=crontab_AMI,
	MinCount=1,
	MaxCount=4,
	KeyName=key_name,
	InstanceType=instance_type)

for instance in instances:
    print(instance.id, instance.instance_type)
