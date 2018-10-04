# Import Package & Module
import boto3
import time
import datetime
import os
from botocore.exceptions import ClientError

#===========================================

# lOG 파일이 존재하는 지 확인하고 없다면 생성한다.
def Log_Checker(path = "./Application.log"):
    if os.path.isfile(path):
        print("존재합니다.")
    else:
        print("새로 만듭니다.")
        with open("Application.log", "w") as f:
            f.write("")

# Log 상태와 상세를 입력하면 추가해줌.
def Log_recorder(status, detail):
    with open("Application.log", "a") as f:
        f.write(str(datetime.datetime.now()) + "\t" + status+ "\t" + detail+"\n")

# ec2객체를 넣으면 vpc_id를 뱉어줌
def VPCid_getter(ec2):
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    return vpc_id

# ec2 객체와 vpc 명을 넣어주면, 보안그룹id를 반환함.
def VPC_generator(ec2,VPC_name='test'):
    response = ec2.create_security_group(GroupName= VPC_name , #'HelloBOTO'
                                         Description='VPC for Testing!',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    return security_group_id

# ec2 객체와, 보안그룹id, 그리고 변환할 tcp port를 두개 넣을 시 변경해준다.
def VPC_ingressor(ec2,security_group_id,tcp_port_A=80,tcp_port_B=143):
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





Log_Checker()
ec2 = boto3.client('ec2')
vpc_id = VPCid_getter(ec2)
tcp_port = [443,143,80,22,20,21,22,23,25,53,70,79,80,110,220,443,20000]

for i in range(10):
    try:
        security_group_id = VPC_generator(ec2,VPC_name=str(i))
        VPC_ingressor(ec2,security_group_id,tcp_port[i],tcp_port[i+1])
        Log_recorder('DONE',security_group_id)
        print("끝났어")
        # time.sleep(5)

    except ClientError as e:
        Log_recorder('ERROR',str(e))
        print("에러가 발생했습니다." + str(e))
        # time.sleep(5)











#v1
# import time
# timeout = time.time() + 60*5   # 5 minutes from now
# while True:
#     test = 0
#     if test == 5 or time.time() > timeout:
#         break
#     test = test - 1

#v2
# timeout = 300   # [seconds]
#
# timeout_start = time.time()
#
# while time.time() < timeout_start + timeout:
#     test = 0
#     if test == 5:
#         break
#     test -= 1

#v3
# from interruptingcow import timeout
# try:
#     with timeout(60*5, exception=RuntimeError):
#         while True:
#             test = 0
#             if test == 5:
#                 break
#             test = test - 1
# except RuntimeError:
#     pass

# exception과 log를 남긴다.

# time.sleep(1)
