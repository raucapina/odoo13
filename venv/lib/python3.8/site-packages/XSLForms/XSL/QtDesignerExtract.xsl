<?xml version="1.0"?>
<!--
An experimental Qt Designer widget extractor for use with QWidgetFactory.

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
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output indent="yes" omit-xml-declaration="yes"/>
  <xsl:param name="widget-name"/>
  <xsl:variable name="widget" select="//widget[property[@name='name' and cstring/text() = $widget-name]]"/>



  <!-- Start at the top, producing a template file. -->

  <xsl:template match="UI">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="$widget"/>
      <xsl:apply-templates select="connections"/>
      <xsl:copy-of select="slots"/>
      <xsl:copy-of select="layoutdefaults"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="widget">
    <xsl:copy>
      <xsl:copy-of select="@class|*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="connections">
    <xsl:copy>
      <xsl:for-each select="connection">
        <xsl:if test="$widget/descendant-or-self::widget[property[@name='name' and (cstring/text() = current()/receiver/text() or cstring/text() = current()/sender/text())]]">
          <xsl:copy-of select="."/>
        </xsl:if>
      </xsl:for-each>
    </xsl:copy>
  </xsl:template>



  <!-- Copy attributes. -->

  <xsl:template match="@*">
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
