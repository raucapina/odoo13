<?xml version="1.0"?>
<!--
A stylesheet which expands the higher-level macro attributes, producing
lower-level attributes that can be translated into the final output stylesheet
code.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>

  <!-- Input fields. -->
  <!-- Format: attribute -->

  <xsl:template match="*[@template:attribute-field]">
    <xsl:copy>
      <!-- Remove attribute-field and replace name and value. -->
      <xsl:apply-templates select="@*[local-name() != 'attribute-field' and local-name() != 'name' and local-name() != 'value']"/>
      <xsl:attribute name="template:attribute"><xsl:value-of select="@template:attribute-field"/></xsl:attribute>
      <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
      <xsl:attribute name="value">{$this-value}</xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Text areas and other elements without value attributes. -->
  <!-- Format: attribute[,effect] -->

  <xsl:template match="*[@template:attribute-area]">
    <xsl:variable name="field-attr" select="substring-before(@template:attribute-area, ',')"/>
    <xsl:variable name="field-effect" select="substring-after(@template:attribute-area, ',')"/>
    <xsl:copy>
      <!-- Remove attribute-area and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'attribute-area' and local-name() != 'name']"/>
      <xsl:choose>
        <xsl:when test="$field-attr != ''">
          <xsl:attribute name="template:attribute"><xsl:value-of select="$field-attr"/></xsl:attribute>
          <xsl:if test="$field-effect != ''">
            <xsl:attribute name="template:effect"><xsl:value-of select="$field-effect"/></xsl:attribute>
          </xsl:if>
          <xsl:attribute name="template:value">$this-value</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="template:attribute"><xsl:value-of select="@template:attribute-area"/></xsl:attribute>
          <xsl:attribute name="template:value">$this-value</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Buttons whose state varies according to an attribute. -->
  <!-- Format: attribute,value,attribute-to-set -->

  <xsl:template match="*[@template:attribute-button]">
    <xsl:variable name="field-attr" select="substring-before(@template:attribute-button, ',')"/>
    <xsl:variable name="field-info" select="substring-after(@template:attribute-button, ',')"/>
    <xsl:variable name="field-value" select="substring-before($field-info, ',')"/>
    <xsl:variable name="field-set-attr" select="substring-after($field-info, ',')"/>
    <xsl:copy>
      <!-- Remove attribute-button and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'attribute-button' and local-name() != 'name']"/>
      <xsl:attribute name="template:attribute"><xsl:value-of select="$field-attr"/></xsl:attribute>
      <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
      <xsl:attribute name="template:expr">$this-value = '<xsl:value-of select="$field-value"/>'</xsl:attribute>
      <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
      <xsl:attribute name="value"><xsl:value-of select="$field-value"/></xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Buttons whose state varies according to an attribute in a list of multiple choice elements. -->
  <!-- Format: attribute,attribute-to-set -->

  <xsl:template match="*[@template:attribute-list-button]">
    <xsl:variable name="field-attr" select="substring-before(@template:attribute-list-button, ',')"/>
    <xsl:variable name="field-set-attr" select="substring-after(@template:attribute-list-button, ',')"/>
    <xsl:copy>
      <!-- Remove attribute-button and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'attribute-button' and local-name() != 'name']"/>
      <xsl:attribute name="template:attribute"><xsl:value-of select="$field-attr"/></xsl:attribute>
      <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
      <xsl:attribute name="template:expr">@value-is-set</xsl:attribute>
      <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
      <xsl:attribute name="value">{$this-value}</xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Selectors. -->
  <!-- Format: name[,affected-element] -->

  <xsl:template match="*[@template:selector-field]">
    <xsl:variable name="field-name" select="substring-before(@template:selector-field, ',')"/>
    <xsl:variable name="affected-element" select="substring-after(@template:selector-field, ',')"/>
    <xsl:copy>
      <!-- Remove selector-field and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'selector-field' and local-name() != 'name']"/>
      <xsl:choose>
        <xsl:when test="$field-name != ''">
          <xsl:attribute name="name"><xsl:value-of select="$field-name"/>={template:this-element()}</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="name"><xsl:value-of select="@template:selector-field"/>={template:this-element()}</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Multiple choice fields, represented by menus and listboxes. -->
  <!-- Format: element,attribute[,attribute-type|,attribute-type,source-type] -->

  <xsl:template match="*[@template:multiple-choice-field]">
    <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-field, ',')"/>
    <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-field, ',')"/>
    <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
    <xsl:variable name="field-attr-type-info" select="substring-after($field-attr-info, ',')"/>
    <xsl:variable name="field-attr-type" select="substring-before($field-attr-type-info, ',')"/>
    <xsl:variable name="field-source-type" select="substring-after($field-attr-type-info, ',')"/>
    <xsl:copy>
      <!-- Remove multiple-choice-field and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'multiple-choice-field' and local-name() != 'name']"/>
      <xsl:if test="$field-element != '-'">
        <xsl:attribute name="template:element"><xsl:value-of select="$field-element"/></xsl:attribute>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="$field-attr-type = 'new' or field-attr-type = '' and $field-attr-type-info = 'new'">
          <xsl:attribute name="name">{template:new-attribute('<xsl:value-of select="$field-attr"/>')}</xsl:attribute>
        </xsl:when>
        <xsl:when test="$field-attr = ''">
          <xsl:attribute name="template:attribute"><xsl:value-of select="$field-attr-info"/></xsl:attribute>
          <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="template:attribute"><xsl:value-of select="$field-attr"/></xsl:attribute>
          <xsl:attribute name="name">{template:this-attribute()}</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Multiple choice list fields, represented by menus and listboxes with multiple values. -->
  <!-- Format: element,list-element,list-attribute[,source-type] -->

  <xsl:template match="*[@template:multiple-choice-list-field]">
    <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-list-field, ',')"/>
    <xsl:variable name="field-list-info" select="substring-after(@template:multiple-choice-list-field, ',')"/>
    <xsl:variable name="field-list-element" select="substring-before($field-list-info, ',')"/>
    <xsl:variable name="field-list-attr-info" select="substring-after($field-list-info, ',')"/>
    <xsl:variable name="field-list-attr" select="substring-before($field-list-attr-info, ',')"/>
    <xsl:variable name="field-source-type" select="substring-after($field-list-attr-info, ',')"/>
    <xsl:copy>
      <!-- Remove multiple-choice-list-field and replace name. -->
      <xsl:apply-templates select="@*[local-name() != 'multiple-choice-list-field' and local-name() != 'name']"/>
      <xsl:if test="$field-element != '-'">
        <xsl:attribute name="template:element"><xsl:value-of select="$field-element"/></xsl:attribute>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="$field-list-attr != ''">
          <xsl:attribute name="name">{template:list-attribute('<xsl:value-of select="$field-list-element"/>',
            '<xsl:value-of select="$field-list-attr"/>')}</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="name">{template:list-attribute('<xsl:value-of select="$field-list-element"/>',
            '<xsl:value-of select="$field-list-attr-info"/>')}</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Multiple choice values, represented by option elements. -->
  <!-- Format: element,attribute,attribute-to-set[,contents-expr] -->

  <xsl:template match="*[@template:multiple-choice-value]">
    <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-value, ',')"/>
    <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-value, ',')"/>
    <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
    <xsl:variable name="field-set-attr-info" select="substring-after($field-attr-info, ',')"/>
    <xsl:variable name="field-set-attr" select="substring-before($field-set-attr-info, ',')"/>
    <xsl:variable name="field-contents" select="substring-after($field-set-attr-info, ',')"/>
    <xsl:copy>
      <!-- Remove multiple-choice-value and replace value. -->
      <xsl:apply-templates select="@*[local-name() != 'multiple-choice-value' and local-name() != 'value']"/>
      <xsl:attribute name="template:element"><xsl:value-of select="$field-element"/></xsl:attribute>
      <xsl:attribute name="template:expr">@<xsl:value-of select="$field-attr"/> = ../@<xsl:value-of select="$field-attr"/></xsl:attribute>
      <!-- For the option text... -->
      <xsl:choose>
        <!-- Either provide the stated attribute as the eventual text of an option element. -->
        <xsl:when test="$field-set-attr = ''">
          <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr-info"/></xsl:attribute>
          <xsl:attribute name="template:value">@<xsl:value-of select="$field-attr"/></xsl:attribute>
        </xsl:when>
        <!-- Or get the specific contents. -->
        <xsl:otherwise>
          <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
          <xsl:attribute name="template:value"><xsl:value-of select="$field-contents"/></xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="value">{@<xsl:value-of select="$field-attr"/>}</xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Multiple choice list values, represented by option elements. -->
  <!-- Format: list-element,list-attribute,attribute-to-set[,contents-expr] -->

  <xsl:template match="*[@template:multiple-choice-list-value]">
    <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-list-value, ',')"/>
    <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-list-value, ',')"/>
    <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
    <xsl:variable name="field-set-attr-info" select="substring-after($field-attr-info, ',')"/>
    <xsl:variable name="field-set-attr" select="substring-before($field-set-attr-info, ',')"/>
    <xsl:variable name="field-contents" select="substring-after($field-set-attr-info, ',')"/>
    <xsl:copy>
      <!-- Remove multiple-choice-value and replace value. -->
      <xsl:apply-templates select="@*[local-name() != 'multiple-choice-list-value' and local-name() != 'value']"/>
      <xsl:attribute name="template:element"><xsl:value-of select="$field-element"/></xsl:attribute>
      <xsl:attribute name="template:expr">@value-is-set</xsl:attribute>
      <!-- For the option text... -->
      <xsl:choose>
        <!-- Either provide the stated attribute as the eventual text of an option element. -->
        <xsl:when test="$field-set-attr = ''">
          <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr-info"/></xsl:attribute>
          <xsl:attribute name="template:value">@<xsl:value-of select="$field-attr"/></xsl:attribute>
        </xsl:when>
        <!-- Or get the specific contents. -->
        <xsl:otherwise>
          <xsl:attribute name="template:expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
          <xsl:attribute name="template:value"><xsl:value-of select="$field-contents"/></xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="value">{@<xsl:value-of select="$field-attr"/>}</xsl:attribute>
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Multiple choice elements. -->
  <!-- Format: element,list-element,list-attribute -->

  <xsl:template match="*[@template:multiple-choice-list-element]">
    <xsl:variable name="element" select="substring-before(@template:multiple-choice-list-element, ',')"/>
    <xsl:variable name="element-list-info" select="substring-after(@template:multiple-choice-list-element, ',')"/>
    <xsl:variable name="element-list-element" select="substring-before($element-list-info, ',')"/>
    <xsl:variable name="element-list-attr" select="substring-after($element-list-info, ',')"/>
    <xsl:copy>
      <!-- Remove multiple-choice-list-element. -->
      <xsl:apply-templates select="@*[local-name() != 'multiple-choice-list-value']"/>
      <xsl:attribute name="template:element"><xsl:value-of select="$element"/>,<xsl:value-of select="$element-list-element"/></xsl:attribute>
      <!-- The attribute is ignored - it is only useful in the schema and input processes. -->
      <xsl:apply-templates select="*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
