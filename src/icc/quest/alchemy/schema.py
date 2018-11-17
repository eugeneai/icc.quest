from .models import *
import colanderalchemy

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("icc.quest")


# class Phones(colander.MappingSchema):
#     number1 = colander.SchemaNode(colander.String(), title=_('Phone1'))
#     number2 = colander.SchemaNode(colander.String(), title=_('Phone2'))
#     number3 = colander.SchemaNode(colander.String(), title=_('Phone3'))


# class Institution(colander.MappingSchema):
#     uuid = colander.SchemaNode(colander.String(), title=_('UUID'))
#     title = colander.SchemaNode(
#         colander.String(), title=_('Full title of organization'))
#     short_title = colander.SchemaNode(
#         colander.String(), title=_('Short title'))
#     tin = colander.SchemaNode(colander.Integer(), title=_('TIN'))
#     rrc = colander.SchemaNode(colander.Integer(), title=_('RRC'))
#     account_details = colander.SchemaNode(
#         colander.String(), title=_('Account details'))
#     details = colander.SchemaNode(
#         colander.String(), title=_('Organization details'))
#     head_name = colander.SchemaNode(colander.String(), title=_('Head name'))
#     head_email = colander.SchemaNode(
#         colander.String(), title=_('Head\'s email'))
#     query_email = colander.SchemaNode(
#         colander.String(), title=_('Query email'))
#     phones = Phones()
#     inst_type_uuid = colander.SchemaNode(colander.String(), title=_('UUID'))
# InstitutionType = colanderalchemy.SQLAlchemySchemaNode(
#     InstitutionType)

# Institution = colanderalchemy.SQLAlchemySchemaNode(Institution)
