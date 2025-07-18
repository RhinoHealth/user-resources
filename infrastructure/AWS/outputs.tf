# --- Outputs ---------------------------------------------------------------------------------------------------------------
# Outputs provide useful information about the deployed infrastructure

output "aws_region" {
  description = "The AWS region"
  value       = var.aws_region
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "The ID of the private subnet"
  value       = aws_subnet.private.id
}

output "ec2_instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "ec2_instance_private_ip" {
  description = "The private IP address of the EC2 instance"
  value       = aws_instance.main.private_ip
}

output "security_group_id" {
  description = "The ID of the security group"
  value       = aws_security_group.main.id
}

output "s3_bucket_output_logs" {
  description = "The name of the output logs S3 bucket"
  value       = aws_s3_bucket.output_logs.bucket
}

output "s3_bucket_source_data" {
  description = "The name of the source data S3 bucket"
  value       = aws_s3_bucket.source_data.bucket
}

output "s3_bucket_logs" {
  description = "The name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket
}

output "cloudwatch_log_group" {
  description = "The name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.name
}

output "cloudtrail_name" {
  description = "The name of the CloudTrail"
  value       = aws_cloudtrail.main.name
}

output "iam_role_arn" {
  description = "The ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2.arn
}

output "nat_gateway_id" {
  description = "The ID of the NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "nat_gateway_public_ip" {
  description = "The public IP address of the NAT Gateway"
  value       = aws_eip.nat.public_ip
}
