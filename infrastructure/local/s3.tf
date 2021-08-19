resource "aws_s3_bucket" "event_dump" {
  bucket        = "event-dump"
  acl = "private"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "events_s3_privacy" {
  bucket = aws_s3_bucket.event_dump.id

  block_public_acls   = true
  block_public_policy = true

  depends_on = [
    aws_s3_bucket.event_dump
  ]
}

resource "aws_s3_bucket_notification" "event_dump" {
  bucket = aws_s3_bucket.event_dump.id

  queue {
    queue_arn     = aws_sqs_queue.some_queue.arn
    events        = ["s3:ObjectCreated:*"]
  }

  depends_on = [
            aws_s3_bucket.event_dump,
            aws_s3_bucket_public_access_block.events_s3_privacy,
            aws_sqs_queue.some_queue
  ]
}
