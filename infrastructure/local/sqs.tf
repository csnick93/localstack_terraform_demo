resource "aws_sqs_queue" "some_queue" {
  name = "some_queue"
  policy = data.aws_iam_policy_document.some_queue.json
}

data "aws_iam_policy_document" "some_queue" {
  policy_id = "__default_policy_ID"
  statement {
    actions = [
      "sqs:SendMessage",
    ]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        "${aws_s3_bucket.event_dump.arn}",
      ]
    }
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
      "*"]
    }
    resources = [
      "arn:aws:sqs:eu-central-1:000000000000:some_queue"
    ]
    sid = "__default_statement_ID"
  }
}
