variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_name" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "db_ssl_mode" {
  type    = string
  default = "require"
}

variable "db_max_connections" {
  type    = number
  default = 100
}

variable "db_connection_timeout" {
  type    = number
  default = 30
}