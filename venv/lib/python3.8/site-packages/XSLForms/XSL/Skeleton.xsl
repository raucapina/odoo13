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
  xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>
  <xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>



  <!-- Match the document itself. -->

  <xsl:template match="/">
    <axsl:stylesheet version="1.0">

      <axsl:output indent="yes"/>

      <axsl:template select="/">

        <!-- Process the elements. -->
        <xsl:apply-templates select="*"/>

      </axsl:template>

    </axsl:stylesheet>
  </xsl:template>



  <!-- Match element references. -->

  <xsl:template match="*[@template:element]">
    <xsl:call-template name="enter-element">
      <xsl:with-param name="other-elements" select="@template:element"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="enter-element">
    <xsl:param name="other-elements"/>
    <xsl:variable name="first-element" select="substring-before($other-elements, ',')"/>
    <xsl:variable name="remaining-elements" select="substring-after($other-elements, ',')"/>
    <xsl:choose>
      <xsl:when test="$first-element = ''">
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$other-elements"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="next-element">
          <xsl:with-param name="first-element" select="$first-element"/>
          <xsl:with-param name="remaining-elements" select="$remaining-elements"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="next-element">
    <xsl:param name="first-element"/>
    <xsl:param name="remaining-elements"/>
    <axsl:for-each select="{$first-element}">
      <axsl:element name="{$first-element}">
      <xsl:choose>
        <xsl:when test="$remaining-elements = ''">
          <xsl:call-template name="enter-attribute"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="enter-element">
            <xsl:with-param name="other-elements" select="$remaining-elements"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
      </axsl:element>
    </axsl:for-each>
  </xsl:template>



  <!-- Match special expression attributes. -->

  <xsl:template match="*[not(@template:element) and @template:attribute]">
    <xsl:call-template name="enter-attribute"/>
  </xsl:template>

  <xsl:template name="enter-attribute">
    <xsl:choose>
      <xsl:when test="@template:attribute">
        <axsl:choose>
          <axsl:when test="@{@template:attribute}">
            <axsl:attribute name="{@template:attribute}"><axsl:value-of select="@{@template:attribute}"/></axsl:attribute>
            <xsl:apply-templates select="*"/>
          </axsl:when>
          <axsl:otherwise>
            <axsl:attribute name="{@template:attribute}"/>
            <xsl:apply-templates select="*"/>
          </axsl:otherwise>
        </axsl:choose>
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
