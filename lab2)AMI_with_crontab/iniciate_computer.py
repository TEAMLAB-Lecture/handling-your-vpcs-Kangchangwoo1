import boto3

ec2 = boto3.resource('ec2', region_name="ap-southeast-1")

outfile = open('please input here','w')
key_pair = ec2.create_key_pair(KeyName='please input here')
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)


#nginx 	ami-0cbad1ff1711f6e1d
#crontab ami-036d344554b4b053a

instances = ec2.create_instances(
	ImageId='ami-0cbad1ff1711f6e1d',
	MinCount=1,
	MaxCount=5,
	KeyName="TestKey",
	InstanceType="t2.micro")

instances = ec2.create_instances(
	ImageId='ami-03221428e6676db69',
	MinCount=1,
	MaxCount=5,
	KeyName="TestKey",
	InstanceType="t2.micro")

for instance in instances:
    print(instance.id, instance.instance_type)
