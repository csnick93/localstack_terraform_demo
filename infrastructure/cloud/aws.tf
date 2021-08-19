variable "region" {
  type = string
  default = "eu-central-1"
}

provider "aws" {
  region = var.region
}
