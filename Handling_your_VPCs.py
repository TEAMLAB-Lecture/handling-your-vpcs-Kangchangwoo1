#============================================================================================================================================
# Import Package & Module
#============================================================================================================================================
import boto3
import time
import datetime
import os
from botocore.exceptions import ClientError
import botocore
#============================================================================================================================================
#============================================================================================================================================


#============================================================================================================================================
# Declear 'Fundamental Function'
#============================================================================================================================================
# lOG 파일이 존재하는 지 확인하고 없다면 생성한다.
def Logfile_Checker(path = "./Application.log"):
    if os.path.isfile(path):
        print("LOG파일이 존재합니다..")
    else:
        print("LOG파일이 존재하지 않습니다.")
        with open("Application.log", "w") as f:
            f.write("")

# Log 상태와 상세를 입력하면 추가해줌.
def Log_recorder(status, detail):
    with open("Application.log", "a") as f:
        f.write(str(datetime.datetime.now()) + "\t" + status+ "\t" + detail+"\n")

# ec2객체를 넣으면 vpc_id를 뱉어줌
def VPCid_getter(ec2):
    return ec2.describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')

# ec2 객체를 넣으면 보안그룹 목록을 뱉어줌
def Security_groups_get(ec2):
    return  [ [value["GroupName"],value["GroupId"]] for value in ec2.describe_security_groups()["SecurityGroups"] ] # value["VpcId"] 는 생략

# ec2 객체와 vpc 명을 넣어주면, 보안그룹id를 반환함.
def VPC_group_generate(ec2,vpc_id='vpc_id',VPC_name='test'):
    response = ec2.create_security_group(GroupName= VPC_name , #'HelloBOTO'
                                         Description='VPC for Testing!',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    return security_group_id

# ec2 객체와, 보안그룹id, 그리고 변환할 tcp port를 두개 넣을 시 변경해준다.
def VPC_group_ingress(ec2,security_group_id,tcp_port_A=80,tcp_port_B=143):
    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': tcp_port_A,
             'ToPort': tcp_port_A, # 80
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', # tcp
             'FromPort': tcp_port_B,
             'ToPort': tcp_port_B, # 22
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)

# ec2 객체와 그룹명을 넣을 경우 보안그룹을 삭제해줌.
def VPC_group_delete(ec2,GroupName):
    ec2.delete_security_group(GroupName=GroupName)

# S3 객체와 버켓명을 넣어주면 있는 지 없는 지 확인해준다.
def S3_bucket_check(Bucket_Name='gachon-bigdata-lecture-201232932kang'):
    s3 = boto3.resource('s3')
    return True if Bucket_Name in [bucket.name for bucket in s3.buckets.all()] else False

# S3 객체와 버켓명, 지역명을 넣으면 버켓을 생성해준다.
def S3_bucket_generate(s3,region_name="ap-southeast-1",Bucket_name='gachon-bigdata-lecture-201232932kang'):
    # s3 = boto3.client('s3', region_name=region_name)
    s3.create_bucket(Bucket=Bucket_name,CreateBucketConfiguration={'LocationConstraint': region_name})

# S3에서 파일을 다운로드 할 떄 활용함.
def S3_file_download(s3, Bucket_name='gachon-bigdata-lecture-201232932kang', remote_path="Application.log", local_path= "Application.log"):
    try:
        s3.download_file(Bucket_name, remote_path,local_path)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

# S3에서 파일을 업로드 할 때 활용함.
def S3_file_upload(s3,Bucket_name='gachon-bigdata-lecture-201232932kang', local_path= "Application.log", remote_path="Application.log"):
    s3.upload_file(local_path, Bucket_name, remote_path)

#============================================================================================================================================
#============================================================================================================================================


#============================================================================================================================================
# Declear 'Level 2 Function'
#============================================================================================================================================

#Problem1
def VPC_geneartor():
    Logfile_Checker()
    ec2 = boto3.client('ec2')
    vpc_id = VPCid_getter(ec2)
    tcp_port = [443,143,80,22,20,21,22,23,25,53,70,79,80,110,220,443,20000]

    for i in range(10):
        try:
            security_group_id = VPC_group_generate(ec2,vpc_id=vpc_id,VPC_name=str(i))
            VPC_group_ingress(ec2,security_group_id,tcp_port[i],tcp_port[i+1])
            Log_recorder('VPC_INSERT_COMPLETED',str(i)+security_group_id)
            print("VPC가 생성되었습니다."+"\t"+str(i)+"\t"+security_group_id)
            time.sleep(5)

        except ClientError as e:
            Log_recorder('ERROR',str(e))
            print("에러가 발생했습니다." + str(e))
            time.sleep(5)

#Problem2
def VPC_deleter():
    Logfile_Checker()
    ec2 = boto3.client('ec2')
    Security_groups = Security_groups_get(ec2)

    for security_group in Security_groups:
        try:
            if security_group[0] != 'default':
                VPC_group_delete(ec2,security_group[0])
                Log_recorder('VPC_DELETE_COMPLETED',security_group[0]+security_group[1])
                print("VPC가 삭제되었습니다."+"\t"+security_group[0]+"\t"+security_group[1])
                # time.sleep(5)
            else:
                Log_recorder('VPC_DELETE_REJECTED',security_group[0]+security_group[1])
                print("defalut로 설정된 VPC는 삭제할 수 없습니다.")

        except ClientError as e:
            Log_recorder('ERROR',str(e))
            print("에러가 발생했습니다." + str(e))

# Problem3
def logfile_uploader():

    s3 = boto3.client('s3', region_name="ap-southeast-1")

    if S3_bucket_check() == False:
        S3_bucket_generate(s3)
        print("원격지에 Bucket이 없기에, 생성했습니다.")


    resource = boto3.resource('s3')
    bucket = resource.Bucket('gachon-bigdata-lecture-201232932kang')

    if 'Application.log' in [ value.key for value in bucket.objects.all() ]:
        print("원격지에 Log파일이 저장되어 있습니다.")
        S3_file_download(s3,local_path="copyed.log")

        c = open("Application.log", 'r')
        lines = c.readlines()

        with open("copyed.log", "a") as f:
            for line in lines:
                f.write(line)

        c.close()

        S3_file_upload(s3,local_path="copyed.log")
        os.remove("copyed.log")

    else:
        print("원격지에 Log 파일을 업로드합니다.")
        S3_file_upload(s3)
        os.remove("Application.log")
#============================================================================================================================================
#============================================================================================================================================


#============================================================================================================================================
# Declear 'Main Function'
#============================================================================================================================================
if __name__ == '__main__':
    VPC_geneartor()
    VPC_deleter()
    logfile_uploader()
#============================================================================================================================================
#============================================================================================================================================
