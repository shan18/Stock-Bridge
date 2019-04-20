import os
import logging


def loan_log(timestamp, username, mode, amount, loan_count, cash, pending_amount):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs',
                        '{}.log'.format(
                            username
                        ))
    logging.basicConfig(filename=path, level=logging.INFO)
    loan_logger = logging.getLogger('{}'.format(username))

    log = '{timestamp}-{username}:{mode} - {amount} - {loan_count} - {cash} - {pending_amount}'.format(
        timestamp=timestamp,
        username=username,
        mode=mode,
        amount=amount,
        loan_count=loan_count,
        cash=cash,
        pending_amount=pending_amount
    )
    loan_logger.info(log)


