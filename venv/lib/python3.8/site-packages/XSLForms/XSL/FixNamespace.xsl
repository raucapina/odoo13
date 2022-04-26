<?xml version="1.0"?>
<!--
Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

  <!-- NOTE: Add various top-level definitions specific to XHTML. -->

  <xsl:output indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    method="xml"/>

  <!-- Get all declared expr-prefix attributes. -->

  <xsl:variable name="prefixes" select="//@expr-prefix"/>



  <!-- Process the root element. -->

  <xsl:template match="/">
    <xsl:for-each select="*">
      <!-- NOTE: Stating the namespace using an explicit xmlns attribute. -->
      <xsl:element name="{name()}">
        <xsl:attribute name="xmlns"><xsl:value-of select="namespace-uri()"/></xsl:attribute>
        <xsl:for-each select="$prefixes">
          <xsl:attribute namespace="{substring-after(string(), ' ')}" name="{substring-before(string(), ' ')}:{name()}"><xsl:value-of select="string()"/></xsl:attribute>
        </xsl:for-each>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:element>
    </xsl:for-each>
  </xsl:template>



  <!-- Remove the mangled template namespace declaration and other declarations. -->

  <xsl:template match="@template|@expr-prefix">
  </xsl:template>



  <!-- Match specific template attributes. -->

  <xsl:template match="@if|@element|@attribute|@attribute-field|@attribute-area|@attribute-button|@attribute-list-button|@selector-field|@multiple-choice-field|@multiple-choice-list-field|@multiple-choice-value|@multiple-choice-list-value|@multiple-choice-list-element|@effect|@value|@expr|@expr-attr|@i18n|@copy">
    <!-- Add the namespace. -->
    <xsl:attribute name="template:{local-name(.)}">
      <xsl:copy-of select="string(.)"/>
    </xsl:attribute>
  </xsl:template>



  <!-- Fix strings in attributes. -->

  <xsl:template name="fix-string">
    <xsl:copy-of select="str:decode-uri(string(.))"/>
  </xsl:template>



  <!-- Handle special attributes. -->

  <xsl:template match="@href|@src">
    <xsl:attribute name="{name(.)}">
      <xsl:call-template name="fix-string"/>
    </xsl:attribute>
  </xsl:template>



  <!-- Traverse unknown nodes. -->

  <xsl:template match="@*|node()">
    <xsl:variable name="this-name" select="name()"/>
    <xsl:if test="not($prefixes[substring-before(string(), ' ') = $this-name])">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
