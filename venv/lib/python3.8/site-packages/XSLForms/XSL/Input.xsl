<?xml version="1.0"?>
<!--
A stylesheet which produces initialisation/input stylesheets for a particular
kind of document.

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
  xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>
  <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>



  <xsl:param name="init-enumerations">yes</xsl:param>



  <!-- Match the document itself. -->

  <xsl:template match="/">
    <axsl:stylesheet version="1.0" xmlns:dyn="http://exslt.org/dynamic"
      extension-element-prefixes="dyn">

      <axsl:output indent="yes"/>

      <!-- Make document parameters for all elements appearing to use enumerations. -->
      <xsl:if test="$init-enumerations = 'yes'">
        <xsl:for-each select="//element[@type='multiple-choice' or @type='multiple-choice-list']">
          <axsl:param name="{@name}"/>
        </xsl:for-each>
      </xsl:if>

      <!-- Make a document-level rule. -->
      <axsl:template match="/">
        <axsl:apply-templates select="*" mode="{generate-id(*[1])}"/>
      </axsl:template>

      <!-- Process the top-level element to make other rules. -->
      <xsl:apply-templates select="*"/>

      <!-- Replicate unknown elements. -->
      <axsl:template match="@*|placeholder|node()">
        <axsl:copy>
          <axsl:apply-templates select="@*|node()"/>
        </axsl:copy>
      </axsl:template>

      <!-- Replicate placeholders for specific elements. -->
      <xsl:for-each select="//element">
        <axsl:template match="placeholder" mode="{generate-id(.)}">
          <axsl:copy>
            <axsl:apply-templates select="@*|node()"/>
          </axsl:copy>
        </axsl:template>
      </xsl:for-each>

    </axsl:stylesheet>
  </xsl:template>



  <!-- Match element references. -->

  <xsl:template match="element">

    <!-- Make a rule for the element. -->
    <axsl:template match="{@name}" mode="{generate-id(.)}">

      <!-- Copy the element. -->
      <xsl:element name="{@name}">

        <!-- Process attributes. -->
        <axsl:apply-templates select="@*"/>

        <!-- Find elements and determine how to process them. -->
        <xsl:call-template name="process-elements"/>
      </xsl:element>
    </axsl:template>

    <!-- Make rules for nested elements. -->
    <xsl:call-template name="process-rules"/>

  </xsl:template>



  <!-- Process elements. -->

  <xsl:template name="process-elements">
    <xsl:param name="path">.</xsl:param>

    <!-- To ensure "stable ordering" of elements, the initialised/static elements are
         added first; the collection/dynamic elements are added afterwards. This may not
         necessarily match the schema, however. -->

    <xsl:for-each select="element|element-ref">
      <!-- Define elements which do not have selectors. -->
      <xsl:variable name="adding-selectors" select="count(//selector[@element=current()/@name])"/>

      <xsl:choose>
        <!-- Recursive element references. -->
        <xsl:when test="local-name(.) = 'element-ref'">
          <axsl:apply-templates select="{@name}" mode="{generate-id(ancestor::element[@name=current()/@name])}"/>
        </xsl:when>
        <!-- Enumerations. -->
        <xsl:when test="@type='multiple-choice-value' or @type='multiple-choice-list-value'">
          <!-- Only generate enumerations if requested. -->
          <xsl:if test="$init-enumerations = 'yes'">
            <xsl:call-template name="inside-enumeration">
              <xsl:with-param name="path" select="concat($path, '/', @name)"/>
            </xsl:call-template>
          </xsl:if>
        </xsl:when>
        <!-- Added elements. -->
        <xsl:when test="(not(@init) or @init = 'auto') and $adding-selectors = 0 or @init = 'yes'">
          <xsl:element name="{@name}">
            <axsl:apply-templates select="{$path}/{@name}/@*"/>
            <xsl:call-template name="process-elements">
              <xsl:with-param name="path" select="concat($path, '/', @name)"/>
            </xsl:call-template>
          </xsl:element>
        </xsl:when>
        <!-- Other elements are only added if found and must appear last - see below. -->
        <xsl:otherwise/>
      </xsl:choose>
    </xsl:for-each>

    <!-- Add the collection/dynamic elements at the end. This includes placeholder
         elements which may have represented the static elements.
         NOTE: We may wish to exclude placeholder elements in any situation where static
         NOTE: elements are employed, since the only place where keeping them around is
         NOTE: necessary/meaningful is in dynamic element collections. -->

    <xsl:call-template name="produce-selection">
      <xsl:with-param name="path" select="$path"/>
      <xsl:with-param name="element" select="element[1]"/>
    </xsl:call-template>

  </xsl:template>



  <!-- Produce a selection of collection/dynamic elements.
       This should produce apply-templates instructions selecting dynamic elements. -->

  <xsl:template name="produce-selection">
    <xsl:param name="path"/>
    <xsl:param name="element"/>

    <xsl:choose>
      <!-- While elements remain... -->
      <xsl:when test="$element">

        <!-- Define elements which do not have selectors. -->
        <xsl:variable name="adding-selectors" select="count(//selector[@element=$element/@name])"/>

        <xsl:choose>
          <!-- Do not select added elements or enumerations - see process-elements. -->
          <xsl:when test="((not($element/@init) or $element/@init = 'auto') and $adding-selectors = 0 or $element/@init = 'yes')
                          or (@type='multiple-choice-value' or @type='multiple-choice-list-value')">
            <xsl:call-template name="produce-selection">
              <xsl:with-param name="path" select="$path"/>
              <xsl:with-param name="element" select="$element/following-sibling::element[1]"/>
            </xsl:call-template>
          </xsl:when>
          <!-- Other elements are only added if found. -->
          <xsl:otherwise>
            <axsl:apply-templates select="{$path}/placeholder|{$path}/{$element/@name}" mode="{generate-id($element)}"/>
            <xsl:call-template name="produce-selection">
              <xsl:with-param name="path" select="$path"/>
              <xsl:with-param name="element" select="$element/following-sibling::element[1]"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <!-- Do nothing when no elements remain. -->
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>



  <!-- Process rules. -->

  <xsl:template name="process-rules">
    <xsl:param name="path">.</xsl:param>

    <xsl:for-each select="element">
      <!-- Define elements which do not have selectors. -->
      <!-- NOTE: Duplicating adding-selectors - see above. -->
      <xsl:variable name="adding-selectors" select="count(//selector[@element=current()/@name])"/>

      <xsl:choose>
        <xsl:when test="@type='multiple-choice-value' or @type='multiple-choice-list-value'">
          <!-- Do not match multiple-choice values. -->
        </xsl:when>
        <xsl:when test="(not(@init) or @init = 'auto') and $adding-selectors = 0 or @init = 'yes'">
          <xsl:call-template name="process-rules">
            <xsl:with-param name="path" select="concat($path, '/', @name)"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="."/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>



  <!-- Fill in enumerations. -->

  <xsl:template name="inside-enumeration">
    <xsl:param name="path"/>

    <!-- Store multiple-choice selections, if appropriate. -->
    <xsl:if test="../@type='multiple-choice-list'">
      <!-- NOTE: It is assumed here that ../attribute/@name (if it exists) == attribute/@name. -->
      <axsl:variable name="values-{@name}" select="{$path}/@{attribute/@name}"/>
    </xsl:if>

    <!-- Select inside the enumeration source, inside an element with the field's name, the enumeration elements. -->
    <xsl:choose>
      <xsl:when test="../@source='dynamic'">
        <axsl:for-each select="dyn:evaluate(${../@name})/{../@name}/{@name}">
          <xsl:call-template name="inside-enumeration-element"/>
        </axsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <axsl:for-each select="${../@name}/{../@name}/{@name}">
          <xsl:call-template name="inside-enumeration-element"/>
        </axsl:for-each>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="inside-enumeration-element">
    <axsl:copy>
      <axsl:apply-templates select="@*"/>
      <xsl:if test="@type='multiple-choice-list-value'">
        <axsl:if test="$values-{@name}[string() = current()/@{attribute/@name}]">
          <axsl:attribute name="{@expr-name}">true</axsl:attribute>
        </axsl:if>
      </xsl:if>
      <!-- Include child nodes, if provided. -->
      <axsl:copy-of select="node()"/>
    </axsl:copy>
  </xsl:template>

</xsl:stylesheet>
