import logging

from dynamic_preferences.users.models import UserPreferenceModel

from magplan.conf import settings as config
from magplan.models import Comment, User


def _get_whitelisted_recipients(pref_name: str) -> set:
    """Get all users, who should receive all
    post comments notifications

    NB: relies on default setting == 'related'!

    :return: Set of users, who we should send
             every comment
    """

    preferences = UserPreferenceModel.objects.prefetch_related('instance').filter(
        section='magplan', name=pref_name, raw_value='all'
    )

    return {p.instance for p in preferences}


def _can_recieve_notification(
        user: User, comment: Comment, perm_name: str, pref_name: str
) -> bool:
    logger = logging.getLogger()
    logger.debug('Checking permissions for recipient %s...' % user.email)

    if not user.has_perm(perm_name):
        logger.debug(
            'Recipient %s decliened as it has no permission to receive post updates.'
            % user.email
        )
        return False

    if user == comment.user:
        logger.debug('Recipient %s decliened as it\'s comment author' % user.email)
        return False

    if config.SYSTEM_USER_ID and user.id == config.SYSTEM_USER_ID:
        logger.debug('Recipient %s decliened as it\'s system user' % user.email)
        return False

    # Disable notification for restricted notification users.
    # This util function is used only in magplan app
    # so it's better to hardcode section name
    # for better re-usabillty
    if user.preferences['magplan__' + pref_name] == 'none':
        logger.debug(
            'Recipient %s decliened as it has turned notifications off' % user.email
        )
        return False

    return True
