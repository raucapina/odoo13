<?xml version="1.0"?>
<!--
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
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>

  <xsl:param name="element-id"/>



  <!-- Start at the top, finding only the specified element. -->

  <xsl:template match="/">
    <xsl:apply-templates select="//*[@template:section=$element-id]"/>
  </xsl:template>



  <!-- Replicate unknown elements. -->

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
