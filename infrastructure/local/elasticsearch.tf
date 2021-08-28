variable "common_prefix"{
    type = string
    description = "Prefix to use for resources"
    default = "default"
}

locals {
  common_prefix = "demo"
  elk_domain = "${var.common_prefix}-elk-domain"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}



## elastic search

resource "aws_elasticsearch_domain" "es" {
  domain_name = "${local.elk_domain}"
  elasticsearch_version = "7.10"

  cluster_config {
      instance_count = 1
      instance_type = "t3.medium.elasticsearch"
      zone_awareness_enabled = false
  }

  ebs_options {
      ebs_enabled = true
      volume_size = 10
  }

  node_to_node_encryption {
    enabled = true
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-0-2019-07"
  }

  advanced_security_options {
      enabled = true
      internal_user_database_enabled = true
      master_user_options {
          master_user_name = "me"
          master_user_password = "password"
      }
  }


  access_policies = <<CONFIG
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Action": "es:*",
          "Principal": "*",
          "Effect": "Allow",
          "Resource": "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${local.elk_domain}/*"
      }
  ]
}
  CONFIG

  snapshot_options {
      automated_snapshot_start_hour = 23
  }

  tags = {
      Domain = local.elk_domain
  }
}

output "elk_endpoint" {
  value = aws_elasticsearch_domain.es.endpoint
}

output "elk_kibana_endpoint" {
  value = aws_elasticsearch_domain.es.kibana_endpoint
}
