# modules/network/variables.tf
variable "cidr_block" {}
variable "public_subnet_cidr" {}
variable "private_subnet_cidr" {}
variable "vpc_name" {
  default = "my-vpc"
}
variable "public_subnet_name" {
  default = "public-subnet"
}

variable "private_subnet_name" {
  default = "private-subnet"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

