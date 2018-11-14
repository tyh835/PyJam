import boto3

def set_s3client(profile=None, **kwargs):
    """
    Keyword Arguments:
        profile: str -- Name of the AWS profile to use (default: None)

    Returns:
        s3: s3.ServiceResource -- Instance of S3 ServiceResource
        session: Session -- Instance of boto3 Session
    """
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    s3 = session.resource('s3')

    return s3, session


