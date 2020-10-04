"""setting up

Revision ID: 6c2f891f5b18
Revises:
Create Date: 2020-10-04 20:45:02.850219+00:00

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '6c2f891f5b18'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

            CREATE TABLE node(
                "data" json NULL,
                is_error bool NOT NULL DEFAULT false,
                node_type varchar(64) NOT NULL,
                created_on timestamp NOT NULL DEFAULT timezone('utc'::text, now()),
                uuid uuid NOT NULL,
                updated_on timestamp NULL DEFAULT timezone('utc'::text, now()),
                CONSTRAINT node_pkey PRIMARY KEY(uuid),
                CONSTRAINT unique_node_uuid UNIQUE(uuid)
            );

            CREATE TABLE node_uuid_to_url(
                url varchar(2044) NULL,
                uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
                CONSTRAINT url UNIQUE(url),
                CONSTRAINT uuid_pkey PRIMARY KEY(uuid)
            );

            CREATE TABLE link(
                updated_on timestamp NOT NULL DEFAULT timezone('utc'::text, now()),
                source_node_uuid uuid NOT NULL,
                target_node_uuid uuid NOT NULL,
                link_type varchar(50) NULL DEFAULT '0'::character varying,
                weight int4 NOT NULL DEFAULT 0,
                CONSTRAINT branches_pkey PRIMARY KEY(source_node_uuid, target_node_uuid)
            );

            CREATE INDEX index ON node_uuid_to_url USING btree(uuid);
            CREATE INDEX index_node_uuid ON link USING btree(target_node_uuid);
            CREATE INDEX index_parent_node_uuid ON link USING btree(source_node_uuid);

            ALTER TABLE node ADD CONSTRAINT lnk__node__node_details FOREIGN KEY(uuid) REFERENCES node_uuid_to_url(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;
            ALTER TABLE link ADD CONSTRAINT lnk__node__relationship_source FOREIGN KEY(source_node_uuid) REFERENCES node_uuid_to_url(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;
            ALTER TABLE link ADD CONSTRAINT lnk__node__relationship_target FOREIGN KEY(target_node_uuid) REFERENCES node_uuid_to_url(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;
        """
    )
    blank_uuid = str(uuid.UUID(int=0))
    op.execute(f"INSERT INTO node_uuid_to_url (url, uuid) VALUES (NULL, '{blank_uuid}');")


def downgrade():
    op.execute(
        """
            ALTER TABLE node DROP CONSTRAINT lnk__node__node_details;
            ALTER TABLE link DROP CONSTRAINT lnk__node__relationship_source;
            ALTER TABLE link DROP CONSTRAINT lnk__node__relationship_target;
            DROP TABLE link;
            DROP TABLE node_uuid_to_url;
            DROP TABLE node;
            DROP EXTENSION "uuid-ossp";
        """
    )
