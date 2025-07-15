provider "aws" {
  region = var.region
}

module "network" {
  source             = "./modules/network"
  cidr_block         = "10.0.0.0/16"
  public_subnet_cidr = "10.0.1.0/24"
}

module "ecs" {
  source                 = "./modules/ecs"
  cluster_name           = "agent-cluster"
  family                 = "agent-service"
  container_definitions  = file("ecs/container_definitions.json")
  cpu                    = 256
  memory                 = 512
  execution_role_arn     = aws_iam_role.ecs_execution.arn
  task_role_arn          = aws_iam_role.ecs_task.arn
}

module "db" {
  source              = "./modules/db"
  name                = "agent-db"
  db_name             = "agentservice"
  username            = var.db_username
  password            = var.db_password
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  subnet_ids          = [module.network.subnet_id]
  security_group_ids  = [aws_security_group.db_access.id]
  publicly_accessible = false
}
