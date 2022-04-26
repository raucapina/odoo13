<?xml version="1.0"?>
<!--
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
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str">

  <xsl:output indent="yes"/>



  <!-- Match the document itself. -->

  <xsl:template match="/">
    <!-- Process the elements. -->
    <xsl:apply-templates select="*"/>
  </xsl:template>



  <!-- Match element references. -->

  <xsl:template match="*[@template:element]" priority="1">
    <xsl:call-template name="enter-element">
      <xsl:with-param name="other-elements" select="@template:element"/>
      <xsl:with-param name="other-init" select="@template:init"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="enter-element">
    <xsl:param name="other-elements"/>
    <xsl:param name="other-init"/>
    <xsl:variable name="first-element" select="substring-before($other-elements, ',')"/>
    <xsl:variable name="remaining-elements" select="substring-after($other-elements, ',')"/>
    <xsl:variable name="first-init" select="substring-before($other-init, ',')"/>
    <xsl:variable name="remaining-init" select="substring-after($other-init, ',')"/>
    <xsl:choose>
      <xsl:when test="$first-element = ''">
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$other-elements"/>
          <xsl:with-param name="first-init" select="$other-init"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$first-element"/>
          <xsl:with-param name="remaining-elements" select="$remaining-elements"/>
          <xsl:with-param name="first-init" select="$first-init"/>
          <xsl:with-param name="remaining-init" select="$remaining-init"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="next-element">
    <xsl:param name="first-element"/>
    <xsl:param name="remaining-elements"/>
    <xsl:param name="first-init"/>
    <xsl:param name="remaining-init"/>
    <!-- Test for recursive references. -->
    <xsl:variable name="recursive-element" select="ancestor::*[$first-element = str:split(@template:element, ',')[1]]"/>
    <xsl:choose>
      <!-- Generate a reference to the previous element definition. -->
      <xsl:when test="$recursive-element">
        <element-ref>
          <xsl:attribute name="name"><xsl:value-of select="$first-element"/></xsl:attribute>
        </element-ref>
      </xsl:when>
      <!-- Generate a normal, nested element definition. -->
      <xsl:otherwise>
        <element>
          <xsl:attribute name="name"><xsl:value-of select="$first-element"/></xsl:attribute>
          <xsl:if test="$first-init != ''">
            <xsl:attribute name="init"><xsl:value-of select="$first-init"/></xsl:attribute>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="$remaining-elements = ''">
              <xsl:call-template name="enter-attribute"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="enter-element">
                <xsl:with-param name="other-elements" select="$remaining-elements"/>
                <xsl:with-param name="other-init" select="$remaining-init"/>
              </xsl:call-template>
            </xsl:otherwise>
          </xsl:choose>
        </element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Match attributes. -->

  <xsl:template match="*[@template:attribute or @template:attribute-field or @template:attribute-area or @template:attribute-button or @template:attribute-list-button or @template:selector-field or @template:multiple-choice-field or @template:multiple-choice-list-field or @template:multiple-choice-value or @template:multiple-choice-list-value or @template:multiple-choice-list-element]">
    <xsl:call-template name="enter-attribute"/>
  </xsl:template>

  <xsl:template name="enter-attribute">
    <xsl:choose>
      <xsl:when test="@template:attribute">
        <attribute>
          <xsl:attribute name="name"><xsl:value-of select="@template:attribute"/></xsl:attribute>
        </attribute>
      </xsl:when>
      <xsl:when test="@template:attribute-field">
        <attribute>
          <xsl:attribute name="name"><xsl:value-of select="@template:attribute-field"/></xsl:attribute>
        </attribute>
      </xsl:when>
      <xsl:when test="@template:attribute-area">
        <attribute>
          <xsl:variable name="field-attr" select="substring-before(@template:attribute-area, ',')"/>
          <xsl:choose>
            <xsl:when test="$field-attr != ''">
              <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
              <xsl:attribute name="name"><xsl:value-of select="@template:attribute-area"/></xsl:attribute>
            </xsl:otherwise>
          </xsl:choose>
        </attribute>
      </xsl:when>
      <xsl:when test="@template:attribute-button">
        <attribute>
          <xsl:variable name="field-attr" select="substring-before(@template:attribute-button, ',')"/>
          <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
        </attribute>
      </xsl:when>
      <xsl:when test="@template:attribute-list-button">
        <attribute>
          <xsl:variable name="field-attr" select="substring-before(@template:attribute-list-button, ',')"/>
          <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
        </attribute>
      </xsl:when>
      <xsl:when test="@template:selector-field">
        <xsl:variable name="field-name" select="substring-before(@template:selector-field, ',')"/>
        <xsl:variable name="affected-element" select="substring-after(@template:selector-field, ',')"/>
        <selector>
          <xsl:choose>
            <xsl:when test="$field-name != ''">
              <xsl:attribute name="name"><xsl:value-of select="$field-name"/></xsl:attribute>
              <xsl:attribute name="element"><xsl:value-of select="$affected-element"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
              <xsl:attribute name="name"><xsl:value-of select="@template:selector-field"/></xsl:attribute>
            </xsl:otherwise>
          </xsl:choose>
        </selector>
      </xsl:when>
      <xsl:when test="@template:multiple-choice-field">
        <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-field, ',')"/>
        <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-field, ',')"/>
        <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
        <xsl:variable name="field-attr-type-info" select="substring-after($field-attr-info, ',')"/>
        <xsl:variable name="field-attr-type" select="substring-before($field-attr-type-info, ',')"/>
        <xsl:variable name="field-source-type" select="substring-after($field-attr-type-info, ',')"/>
        <xsl:choose>
          <xsl:when test="$field-element != '-'">
            <element type="multiple-choice">
              <xsl:attribute name="name"><xsl:value-of select="$field-element"/></xsl:attribute>
              <xsl:if test="$field-source-type = 'dynamic'">
                <xsl:attribute name="source">dynamic</xsl:attribute>
              </xsl:if>
              <attribute>
                <xsl:choose>
                  <xsl:when test="$field-attr != ''">
                    <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:attribute name="name"><xsl:value-of select="$field-attr-info"/></xsl:attribute>
                  </xsl:otherwise>
                </xsl:choose>
              </attribute>
              <xsl:apply-templates select="*"/>
            </element>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="type">multiple-choice</xsl:attribute>
            <xsl:if test="$field-source-type = 'dynamic'">
              <xsl:attribute name="source">dynamic</xsl:attribute>
            </xsl:if>
            <attribute>
              <xsl:choose>
                <xsl:when test="$field-attr != ''">
                  <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="name"><xsl:value-of select="$field-attr-info"/></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
            </attribute>
            <xsl:apply-templates select="*"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="@template:multiple-choice-list-field">
        <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-list-field, ',')"/>
        <xsl:variable name="field-list-info" select="substring-after(@template:multiple-choice-list-field, ',')"/>
        <xsl:variable name="field-list-element" select="substring-before($field-list-info, ',')"/>
        <xsl:variable name="field-list-attr-info" select="substring-after($field-list-info, ',')"/>
        <xsl:variable name="field-list-attr" select="substring-before($field-list-attr-info, ',')"/>
        <xsl:variable name="field-source-type" select="substring-after($field-list-attr-info, ',')"/>
        <xsl:choose>
          <xsl:when test="$field-element != '-'">
            <element type="multiple-choice-list">
              <xsl:attribute name="name"><xsl:value-of select="$field-element"/></xsl:attribute>
              <xsl:if test="$field-source-type = 'dynamic'">
                <xsl:attribute name="source">dynamic</xsl:attribute>
              </xsl:if>
              <attribute>
                <xsl:attribute name="name"><xsl:value-of select="$field-list-attr"/></xsl:attribute>
              </attribute>
              <xsl:apply-templates select="*"/>
            </element>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="type">multiple-choice-list</xsl:attribute>
            <xsl:if test="$field-source-type = 'dynamic'">
              <xsl:attribute name="source">dynamic</xsl:attribute>
            </xsl:if>
            <attribute>
              <xsl:attribute name="name"><xsl:value-of select="$field-list-attr"/></xsl:attribute>
            </attribute>
            <xsl:apply-templates select="*"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="@template:multiple-choice-list-element">
        <xsl:variable name="element" select="substring-before(@template:multiple-choice-list-element, ',')"/>
        <xsl:variable name="element-list-info" select="substring-after(@template:multiple-choice-list-element, ',')"/>
        <xsl:variable name="element-list-element" select="substring-before($element-list-info, ',')"/>
        <xsl:variable name="element-list-attr" select="substring-after($element-list-info, ',')"/>
        <xsl:choose>
          <xsl:when test="$element != '-'">
            <element type="multiple-choice-list">
              <xsl:attribute name="name"><xsl:value-of select="$element"/></xsl:attribute>
              <element type="multiple-choice-list-value">
                <xsl:attribute name="name"><xsl:value-of select="$element-list-element"/></xsl:attribute>
                <xsl:attribute name="expr-name">value-is-set</xsl:attribute>
                <xsl:apply-templates select="*"/>
              </element>
            </element>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="type">multiple-choice-list</xsl:attribute>
            <element type="multiple-choice-list-value">
              <xsl:attribute name="name"><xsl:value-of select="$element-list-element"/></xsl:attribute>
              <xsl:attribute name="expr-name">value-is-set</xsl:attribute>
              <xsl:apply-templates select="*"/>
            </element>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="@template:multiple-choice-value">
        <element type="multiple-choice-value">
          <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-value, ',')"/>
          <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-value, ',')"/>
          <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
          <xsl:variable name="field-set-attr-info" select="substring-after($field-attr-info, ',')"/>
          <xsl:variable name="field-set-attr" select="substring-before($field-set-attr-info, ',')"/>
          <xsl:variable name="field-contents" select="substring-after($field-set-attr-info, ',')"/>
          <xsl:attribute name="name"><xsl:value-of select="$field-element"/></xsl:attribute>
          <xsl:attribute name="expr">@<xsl:value-of select="$field-attr"/> = ../@<xsl:value-of select="$field-attr"/></xsl:attribute>
          <xsl:choose>
            <xsl:when test="$field-set-attr != ''">
              <xsl:attribute name="expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
              <xsl:attribute name="expr-attr"><xsl:value-of select="$field-set-attr-info"/></xsl:attribute>
            </xsl:otherwise>
          </xsl:choose>
          <attribute>
            <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
          </attribute>
        </element>
      </xsl:when>
      <xsl:when test="@template:multiple-choice-list-value">
        <element type="multiple-choice-list-value">
          <xsl:variable name="field-element" select="substring-before(@template:multiple-choice-list-value, ',')"/>
          <xsl:variable name="field-attr-info" select="substring-after(@template:multiple-choice-list-value, ',')"/>
          <xsl:variable name="field-attr" select="substring-before($field-attr-info, ',')"/>
          <xsl:variable name="field-set-attr-info" select="substring-after($field-attr-info, ',')"/>
          <xsl:variable name="field-set-attr" select="substring-before($field-set-attr-info, ',')"/>
          <xsl:variable name="field-contents" select="substring-after($field-set-attr-info, ',')"/>
          <xsl:attribute name="name"><xsl:value-of select="$field-element"/></xsl:attribute>
          <xsl:attribute name="expr">@value-is-set</xsl:attribute>
          <!-- Special attribute corresponding with the expression. -->
          <xsl:attribute name="expr-name">value-is-set</xsl:attribute>
          <xsl:choose>
            <xsl:when test="$field-set-attr != ''">
              <xsl:attribute name="expr-attr"><xsl:value-of select="$field-set-attr"/></xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
              <xsl:attribute name="expr-attr"><xsl:value-of select="$field-set-attr-info"/></xsl:attribute>
            </xsl:otherwise>
          </xsl:choose>
          <attribute>
            <xsl:attribute name="name"><xsl:value-of select="$field-attr"/></xsl:attribute>
          </attribute>
        </element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="*"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Traverse unknown elements. -->

  <xsl:template match="*">
    <xsl:apply-templates select="*"/>
  </xsl:template>

</xsl:stylesheet>
