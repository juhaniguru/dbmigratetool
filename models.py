from typing import List

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = (
        Index('category_name_UNIQUE', 'category_name', unique=True),
    )

    categoryID = mapped_column(Integer, primary_key=True)
    category_name = mapped_column(String(45), nullable=False)

    product: Mapped[List['Product']] = relationship('Product', uselist=True, back_populates='category')


class Feature(Base):
    __tablename__ = 'feature'
    __table_args__ = (
        Index('feature_name_UNIQUE', 'feature_name', unique=True),
    )

    featureID = mapped_column(Integer, primary_key=True)
    feature_name = mapped_column(String(45), nullable=False)

    product_has_feature: Mapped[List['ProductHasFeature']] = relationship('ProductHasFeature', uselist=True, back_populates='feature')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        Index('role_UNIQUE', 'role_name', unique=True),
    )

    roleID = mapped_column(Integer, primary_key=True)
    role_name = mapped_column(String(45), nullable=False)

    auth_user: Mapped[List['AuthUser']] = relationship('AuthUser', uselist=True, back_populates='role')


class State(Base):
    __tablename__ = 'state'
    __table_args__ = (
        Index('state_name_UNIQUE', 'state_name', unique=True),
    )

    stateID = mapped_column(Integer, primary_key=True)
    state_name = mapped_column(String(45), nullable=False)

    product: Mapped[List['Product']] = relationship('Product', uselist=True, back_populates='state')


class AuthUser(Base):
    __tablename__ = 'auth_user'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['role.roleID'], name='fk_user_role'),
        Index('fk_user_role_idx', 'role_id'),
        Index('username_UNIQUE', 'username', unique=True)
    )

    userID = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(45), nullable=False)
    password = mapped_column(String(255), nullable=False)
    role_id = mapped_column(Integer, nullable=False)
    access_jti = mapped_column(String(45))

    role: Mapped['Role'] = relationship('Role', back_populates='auth_user')
    commerce_transaction: Mapped[List['CommerceTransaction']] = relationship('CommerceTransaction', uselist=True, back_populates='buyer')
    product: Mapped[List['Product']] = relationship('Product', uselist=True, back_populates='seller')


class CommerceTransaction(Base):
    __tablename__ = 'commerce_transaction'
    __table_args__ = (
        ForeignKeyConstraint(['buyer_id'], ['auth_user.userID'], name='fk_commerce_transaction_user1'),
        Index('fk_commerce_transaction_user1_idx', 'buyer_id')
    )

    transactionID = mapped_column(Integer, primary_key=True)
    buyer_id = mapped_column(Integer, nullable=False)
    sold_at = mapped_column(DateTime, nullable=False)
    sold_price = mapped_column(Integer, nullable=False)

    buyer: Mapped['AuthUser'] = relationship('AuthUser', back_populates='commerce_transaction')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['category.categoryID'], name='fk_product_category1'),
        ForeignKeyConstraint(['seller_id'], ['auth_user.userID'], name='fk_product_user1'),
        ForeignKeyConstraint(['state_id'], ['state.stateID'], name='fk_product_state1'),
        Index('fk_product_category1_idx', 'category_id'),
        Index('fk_product_state1_idx', 'state_id'),
        Index('fk_product_user1_idx', 'seller_id')
    )

    productID = mapped_column(Integer, primary_key=True)
    product_name = mapped_column(String(45), nullable=False)
    category_id = mapped_column(Integer, nullable=False)
    seller_id = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime, nullable=False)
    state_id = mapped_column(Integer, nullable=False)
    price = mapped_column(Integer, nullable=False)
    product_description = mapped_column(Text)

    category: Mapped['Category'] = relationship('Category', back_populates='product')
    seller: Mapped['AuthUser'] = relationship('AuthUser', back_populates='product')
    state: Mapped['State'] = relationship('State', back_populates='product')
    product_has_feature: Mapped[List['ProductHasFeature']] = relationship('ProductHasFeature', uselist=True, back_populates='product')


class ProductHasFeature(Base):
    __tablename__ = 'product_has_feature'
    __table_args__ = (
        ForeignKeyConstraint(['feature_featureID'], ['feature.featureID'], name='fk_product_has_feature_feature1'),
        ForeignKeyConstraint(['product_productID'], ['product.productID'], name='fk_product_has_feature_product1'),
        Index('fk_product_has_feature_feature1_idx', 'feature_featureID'),
        Index('fk_product_has_feature_product1_idx', 'product_productID')
    )

    product_productID = mapped_column(Integer, primary_key=True, nullable=False)
    feature_featureID = mapped_column(Integer, primary_key=True, nullable=False)
    value = mapped_column(String(45), nullable=False)

    feature: Mapped['Feature'] = relationship('Feature', back_populates='product_has_feature')
    product: Mapped['Product'] = relationship('Product', back_populates='product_has_feature')
