terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. The Network (VPC)
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "pulseops-vpc"
  }
}

# 2. The Database (RDS PostgreSQL)
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  db_name              = "jobs_db"
  username             = var.db_username
  password             = var.db_password # Injected via CI/CD or Secrets Manager
  skip_final_snapshot  = true
}

# 3. The Redis Queue (ElastiCache)
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "pulseops-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}