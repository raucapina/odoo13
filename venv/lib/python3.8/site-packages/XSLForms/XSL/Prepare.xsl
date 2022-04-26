<?xml version="1.0"?>
<!--
A stylesheet which takes lower-level template annotations and produces an output
stylesheet - something which is capable of transforming XML documents into Web
pages or other kinds of XML documents.

Copyright (C) 2005, 2007 Paul Boddie <paul@boddie.org.uk>

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
  xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template"
  xmlns:str="http://exslt.org/strings"
  extension-element-prefixes="str">

  <xsl:output indent="yes"/>
  <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>

  <!-- Fragment extraction support. -->
  <xsl:param name="element-id"/>

  <!-- Match the document itself. -->

  <xsl:template match="/">
    <axsl:stylesheet version="1.0"
      xmlns:dyn="http://exslt.org/dynamic"
      extension-element-prefixes="dyn">

      <!-- Add support for special namespace declarations. -->
      <xsl:for-each select="//@*[local-name() = 'expr-prefix']">
        <xsl:attribute namespace="{namespace-uri()}" name="{name(.)}"></xsl:attribute>
      </xsl:for-each>

      <axsl:output indent="yes"/>

      <!-- Include internationalisation (i18n) support if appropriate. -->
      <axsl:param name="translations"/>
      <axsl:param name="locale"/>

      <!-- Include fragment support if appropriate. -->
      <axsl:param name="element-path"/>

      <axsl:template match="/">
        <xsl:choose>
          <!-- Fragment production. -->
          <xsl:when test="$element-id != ''">
            <axsl:for-each select="dyn:evaluate($element-path)">
              <xsl:apply-templates select="@*|node()"/>
            </axsl:for-each>
          </xsl:when>
          <!-- Whole template production. -->
          <xsl:otherwise>
            <xsl:apply-templates select="@*|node()"/>
          </xsl:otherwise>
        </xsl:choose>
      </axsl:template>

      <!-- Produce the rules for each element. -->

      <xsl:apply-templates select="//*[@template:element]">
        <xsl:with-param name="top-level">true</xsl:with-param>
      </xsl:apply-templates>

    </axsl:stylesheet>
  </xsl:template>



  <!-- Match elements referencing elements. -->

  <xsl:template match="*[@template:element]" priority="1">
    <xsl:param name="top-level">false</xsl:param>
    <xsl:call-template name="enter-element">
      <xsl:with-param name="top-level" select="$top-level"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="enter-element">
    <xsl:param name="top-level"/>
    <xsl:choose>
      <!-- Produce templates where this is a top-level definition. -->
      <xsl:when test="$top-level = 'true'">
        <xsl:call-template name="element-template">
          <xsl:with-param name="element-names" select="@template:element"/>
        </xsl:call-template>
      </xsl:when>
      <!-- Produce references to elements where this is within a template. -->
      <xsl:otherwise>
        <xsl:variable name="first-name" select="str:split(@template:element, ',')[1]"/>
        <!-- Check to see if this is a recursive reference. -->
        <xsl:variable name="recursive-element" select="ancestor::*[$first-name = str:split(@template:element, ',')[1]]"/>
        <xsl:choose>
          <!-- Generate a reference to the previous element definition. -->
          <xsl:when test="$recursive-element">
            <axsl:apply-templates select="{$first-name}" mode="{generate-id($recursive-element)}"/>
          </xsl:when>
          <!-- Generate a reference to this element definition. -->
          <xsl:otherwise>
            <axsl:apply-templates select="{$first-name}" mode="{generate-id(.)}"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="element-template">
    <xsl:param name="element-names"/>
    <xsl:variable name="this-name" select="substring-before($element-names, ',')"/>
    <xsl:variable name="next-names" select="substring-after($element-names, ',')"/>
    <xsl:variable name="next-name" select="str:split($next-names, ',')[1]"/>
    <xsl:choose>
      <!-- Non-last part of a list of element names. -->
      <!-- Produce a template referencing another template. -->
      <xsl:when test="$this-name != ''">
        <!-- Produce a template with a mode. -->
        <axsl:template match="{$this-name}" mode="{generate-id(.)}">
          <axsl:apply-templates select="{$next-name}" mode="{generate-id(.)}"/>
        </axsl:template>
        <!-- Produce the other elements' templates... -->
        <xsl:call-template name="element-template">
          <xsl:with-param name="element-names" select="$next-names"/>
        </xsl:call-template>
      </xsl:when>
      <!-- Last part of a list of element names. -->
      <!-- Produce a template with content. -->
      <xsl:otherwise>
        <!-- Produce a template with a mode. -->
        <axsl:template match="{$element-names}" mode="{generate-id(.)}">
          <xsl:call-template name="enter-attribute"/>
        </axsl:template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Match special conditional expression attributes. -->

  <xsl:template match="*[@template:if]" priority="2">
    <xsl:param name="top-level">false</xsl:param>
    <xsl:choose>
      <!-- Since this rule may be invoked at the top level, ignore conditions. -->
      <xsl:when test="$top-level = 'true'">
        <xsl:call-template name="enter-element">
          <xsl:with-param name="top-level" select="$top-level"/>
        </xsl:call-template>
      </xsl:when>
      <!-- As part of a template, generate the condition. -->
      <xsl:otherwise>
        <axsl:if test="{@template:if}">
          <xsl:choose>
            <xsl:when test="@template:element">
              <xsl:call-template name="enter-element"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="enter-attribute"/>
            </xsl:otherwise>
          </xsl:choose>
        </axsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Match special expression attributes. -->

  <xsl:template match="*[@template:attribute or @template:value or @template:expr or @template:copy]">
    <xsl:call-template name="enter-attribute"/>
  </xsl:template>

  <xsl:template name="enter-attribute">
    <xsl:choose>
      <xsl:when test="@template:attribute">
        <axsl:choose>
          <axsl:when test="@{@template:attribute}">
            <axsl:variable name="this-name"><xsl:value-of select="@template:attribute"/></axsl:variable>
            <axsl:variable name="this-value" select="@{@template:attribute}"/>
            <xsl:call-template name="special-attributes"/>
          </axsl:when>
          <axsl:otherwise>
            <axsl:variable name="this-name"><xsl:value-of select="@template:attribute"/></axsl:variable>
            <axsl:variable name="this-value"></axsl:variable>
            <xsl:call-template name="special-attributes"/>
          </axsl:otherwise>
        </axsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="special-attributes"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="special-attributes">
    <xsl:choose>
      <xsl:when test="@template:effect = 'replace'">
        <xsl:call-template name="special-value"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates select="@*"/>
          <xsl:call-template name="expression-attributes"/>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="expression-attributes">
    <xsl:if test="@template:expr and @template:expr-attr">
      <axsl:if test="{@template:expr}">
        <axsl:attribute name="{@template:expr-attr}"><xsl:value-of select="@template:expr-attr"/></axsl:attribute>
      </axsl:if>
    </xsl:if>
    <xsl:call-template name="special-value"/>
  </xsl:template>

  <xsl:template name="special-value">
    <xsl:choose>
      <!-- Insert the translated value. -->
      <xsl:when test="@template:i18n">
        <xsl:call-template name="translated-value"/>
      </xsl:when>
      <!-- Insert the stated value. -->
      <xsl:when test="@template:value">
        <axsl:value-of select="{@template:value}"/>
      </xsl:when>
      <!-- Copy the stated expression. -->
      <xsl:when test="@template:copy">
        <axsl:copy-of select="{@template:copy}"/>
      </xsl:when>
      <!-- Just process the descendants. -->
      <xsl:otherwise>
        <xsl:apply-templates select="node()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!-- Match internationalisation attributes. -->

  <xsl:template match="*[not(@template:if) and not(@template:element) and not(@template:attribute) and not(@template:value) and not(@template:expr) and @template:i18n]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:call-template name="translated-value"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template name="translated-value">
    <xsl:choose>
      <!-- Look for a translation of the contents. -->
      <xsl:when test="@template:i18n = '-'">
        <!-- NOTE: Quoting not done completely. -->
        <axsl:variable name="translation"
          select="$translations/translations/locale[code/@value=$locale]/translation[@value='{text()}']/text()"/>
        <axsl:variable name="translation-default"
          select="$translations/translations/locale[1]/translation[@value='{text()}']/text()"/>
        <xsl:call-template name="insert-translated-value"/>
      </xsl:when>
      <!-- Look for a translation based on the expression. -->
      <xsl:when test="starts-with(@template:i18n, '{') and substring(@template:i18n, string-length(@template:i18n), 1) = '}'">
        <!-- Select the expression. -->
        <axsl:variable name="i18n-expr" select="{substring(@template:i18n, 2, string-length(@template:i18n) - 2)}"/>
        <!-- Translate according to the expression. -->
        <axsl:variable name="translation"
          select="$translations/translations/locale[code/@value=$locale]/translation[@value=$i18n-expr]/text()"/>
        <axsl:variable name="translation-default"
          select="$translations/translations/locale[1]/translation[@value=$i18n-expr]/text()"/>
        <xsl:call-template name="insert-translated-value">
          <xsl:with-param name="default">$i18n-expr</xsl:with-param>
        </xsl:call-template>
      </xsl:when>
      <!-- Look for a named translation. -->
      <xsl:otherwise>
        <!-- NOTE: Quoting not done completely. -->
        <axsl:variable name="translation"
          select="$translations/translations/locale[code/@value=$locale]/translation[@value='{@template:i18n}']/text()"/>
        <axsl:variable name="translation-default"
          select="$translations/translations/locale[1]/translation[@value='{@template:i18n}']/text()"/>
        <xsl:call-template name="insert-translated-value"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="insert-translated-value">
    <xsl:param name="default"/>
    <axsl:choose>
      <!-- Insert the translated value. -->
      <axsl:when test="$translation">
        <axsl:value-of select="$translation"/>
      </axsl:when>
      <!-- Or insert the default translated value. -->
      <axsl:when test="$translation-default">
        <axsl:value-of select="$translation-default"/>
      </axsl:when>
      <!-- Otherwise, just process the descendants. -->
      <axsl:otherwise>
        <xsl:choose>
          <xsl:when test="$default">
            <axsl:value-of select="{$default}"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="node()"/>
          </xsl:otherwise>
        </xsl:choose>
      </axsl:otherwise>
    </axsl:choose>
  </xsl:template>



  <!-- Remove template attributes. -->

  <xsl:template match="@template:element|@template:init|@template:attribute|@template:value|@template:expr|@template:expr-attr|@template:effect|@template:if|@template:i18n|@template:copy">
  </xsl:template>



  <!-- Remove special attributes for preserving namespace prefixes used in expressions. -->

  <xsl:template match="@*[local-name() = 'expr-prefix']">
  </xsl:template>



  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
