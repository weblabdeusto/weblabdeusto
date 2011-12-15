<%@ Page language="c#" Inherits="iLabs.Services.SelfRegistration" CodeFile="SelfRegistration.aspx.cs" EnableEventValidation="false" %>
<%@ Register Assembly="iLabControls" Namespace="iLabs.Controls" TagPrefix="iLab" %>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" >
<HTML>
	<HEAD>
		<title>selfRegistration</title> 
		<!-- 
Copyright (c) 2004 The Massachusetts Institute of Technology. All rights reserved.
Please see license.txt in top level directory for full license. 
-->
		<meta content="Microsoft Visual Studio .NET 7.1" name="GENERATOR">
		<meta content="C#" name="CODE_LANGUAGE">
		<meta content="JavaScript" name="vs_defaultClientScript">
		<meta content="http://schemas.microsoft.com/intellisense/ie5" name="vs_targetSchema">
		<style type="text/css">@import url( css/main.css );
		</style>
	</HEAD>
	<body>
	    <form id="Form1" method="post" runat="server">
	    <a name="top"></a>
	    <div id="outerwrapper">
		<div id="innerwrapper">
				<iLab:RegisterSelf ID="selfReg" runat="server" AgentType="LAB SERVER" />		
		</div><!-- end innerwrapper div -->
		<br clear="all" />
		</div>
		</form>
	</body>
</HTML>
