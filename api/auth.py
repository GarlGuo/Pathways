
# This file contains utilities for interacting with Cornell's Shibboleth IDP
# to provide authentication to your application.
from urllib.parse import urlparse

from flask import redirect, make_response

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.metadata import OneLogin_Saml2_Metadata
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser


def init_auth(idp_metadata, metadata_endpoint, consumer_endpoint):
    """Use this function to initialize an auth object that will be passed into the utilities given in this module.
    :param idp_metadata: URL of the IdP's metadata file.
    :param metadata_endpoint: the GET endpoint of your application that should directly serve the output of serve_metadata.
    :param consumer_endpoint: the POST endpoint of your application that the user is redirected to after successfully logging in.
    """
    return {
        "idp_metadata": idp_metadata,
        "metadata_endpoint": metadata_endpoint,
        "consumer_endpoint": consumer_endpoint,
    }


def serve_sso_redirect(req, auth, token=""):
    """Returns a Flask redirect to the authentication page."""
    _auth = auth.copy()
    # if a token is passed, make sure auth redirects with that token
    if token != "":
        _auth["consumer_endpoint"] += "?token=" + token
    auth = OneLogin_Saml2_Auth(__prepare_flask_request(req), __get_auth_settings(_auth))
    sso_built_url = auth.login()
    return sso_built_url


def consume_response(req, auth):
    """Consumes the response at the consumer endpoint and returns an object with useful data about the authenticated user.
    The returned object returns some raw SAML fields, as well as the following user data (key -> value):
    * netId -> the user's netId
    * email -> the user's Cornell email
    * affiliations -> an array containing the user's university affiliations (roles)
    * primaryAffiliation -> the user's primary university affiliations (role)
    * displayName -> the user's friendly display name
    * fullName -> the user's full name
    * firstName -> the user's first name
    * lastName -> the user's surname (last name)
    """
    auth = OneLogin_Saml2_Auth(__prepare_flask_request(req), __get_auth_settings(auth))
    auth.process_response()
    errors = auth.get_errors()
    if len(errors) == 0:
        return {
            "errored": False,
            "samlUserdata": auth.get_attributes(),
            "samlNameId": auth.get_nameid(),
            "samlNameIdFormat": auth.get_nameid_format(),
            "samlNameIdQualifier": auth.get_nameid_nq(),
            "samlNameIdSPNameQualifier": auth.get_nameid_spnq(),
            "samlSessionIndex": auth.get_session_index(),

            # To make things easier, we'll unpack some of the attributes here.
            # The full list of attribute names and their meanings is located here:
            # https://blogs.cornell.edu/cloudification/2016/07/11/using-cornell-shibboleth-for-authentication-in-your-custom-application/
            "netId": auth.get_attribute("urn:oid:0.9.2342.19200300.100.1.1")[0],
            "email": auth.get_attribute("urn:oid:0.9.2342.19200300.100.1.3")[0],
            "affiliations": auth.get_attribute("urn:oid:1.3.6.1.4.1.5923.1.1.1.1"),
            "primaryAffiliation": auth.get_attribute(
                "urn:oid:1.3.6.1.4.1.5923.1.1.1.5"
            )[0],
            "displayName": auth.get_attribute("urn:oid:2.16.840.1.113730.3.1.241")[
                0
            ],
            "fullName": auth.get_attribute("urn:oid:2.5.4.3")[0],
            "lastName": auth.get_attribute("urn:oid:2.5.4.4")[0],
            "firstName": auth.get_attribute("urn:oid:2.5.4.42")[0],
        }
    else:
        return {"errored": True, "reason": auth.get_last_error_reason()}


def serve_metadata(auth):
    """Returns a Flask response that serves our SP's metadata in XML.
    """
    metadata = OneLogin_Saml2_Metadata.builder(__get_auth_settings(auth))
    resp = make_response(metadata, 200)
    resp.headers["Content-Type"] = "text/xml"
    return resp


def __prepare_flask_request(request):
    # Converts a Flask request to a OneLogin request parameter.
    url_data = urlparse(request.url)
    return {
        "https": "on" if request.scheme == "https" else "off",
        "http_host": request.host,
        "server_port": url_data.port,
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
    }


def __get_auth_settings(auth):
    # For this to work, we need a metadata object that contains information about
    # both the IdP and our application (the SP). The IdP metadata is taken directly
    # from the IdP's metadata endpoint, but we must append our SP's metadata before returning
    # the final object.

    # Get the IdP's metadata.
    settings = OneLogin_Saml2_IdPMetadataParser.parse_remote(auth["idp_metadata"])

    # Define the SP's metadata; these values are predetermined.
    settings["sp"]["entityId"] = auth["metadata_endpoint"]
    settings["sp"]["assertionConsumerService"] = {
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        "url": auth["consumer_endpoint"],
    }
    settings[
        "authn_context"
    ] = "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
    settings["sp"]["NameIDFormat"] = "urn:mace:shibboleth:1.0:nameIdentifier"
    return settings

