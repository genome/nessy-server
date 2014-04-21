ALTER TYPE foo RENAME TO claim_status_enum;
ALTER TYPE claim_status_enum ADD VALUE 'aborted';
ALTER TYPE claim_status_enum ADD VALUE 'withdrawn';
