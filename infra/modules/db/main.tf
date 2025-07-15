variable "name" {}
variable "db_name" {}
variable "username" {}
variable "password" {}
variable "instance_class" {
  default = "db.t3.micro"
}
variable "allocated_storage" {
  default = 20
}
variable "subnet_ids" {
  type = list(string)
}
variable "security_group_ids" {
  type = list(string)
}
variable "publicly_accessible" {
  default = false
}

variable "engine" {
  default = "mysql"
}
variable "engine_version" {
  default = "8.0"
}
variable "parameter_group_name" {
  default = "default.mysql8.0"
}
variable "backup_retention_period" {
  default = 7
}
variable "multi_az" {
  default = false
}