%{?_javapackages_macros:%_javapackages_macros}

%define oname mac_widgets
%define name %(echo %{oname} | tr -cd [:alnum:])

Summary:	Collection of Mac style widgets written in Java
Name:		%{name}
Version:	0.10.0
Release:	1
License:	LGPLv3
Group:		Development/Java
URL:		https://code.google.com/p/macwidgets/
# svn checkout http://macwidgets.googlecode.com/svn/trunk/ macwidgets-r417
# cp -far macwidgets-r417 macwidgets-0.10.0
# find macwidgets-0.10.0 -name \.svn -type d -exec rm -fr ./{} \; 2> /dev/null
# tar Jcf macwidgets-0.10.0.tar.xz macwidgets-0.10.0
Source0:	%{name}-%{version}.tar.xz
Source1:	https://repo1.maven.org/maven2/com/explodingpixels/%{oname}/0.9.5/%{oname}-0.9.5.pom
BuildArch:	noarch

BuildRequires:	maven-local
BuildRequires:	mvn(com.jgoodies:jgoodies-forms)
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.codehaus.mojo:build-helper-maven-plugin)

%description
Mac Widgets for Java are a collection of widgets seen in OS X applications,
offered in a Java API. These widgets help Java developers create more Mac-like
applications.

Their usage is not restricted to Mac though, as they will render across
platforms. 

%files -f .mfiles

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for Mac Widgets.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q
# Delete all prebuild JARs and classes
find . -name "*.jar" -delete
find . -name "*.class" -delete

# pom.xml
cp %{SOURCE1} ./pom.xml

# Change artifact and version to the current one
%pom_xpath_replace "pom:project/pom:artifactId" "<artifactId>%{name}</artifactId>"
%pom_xpath_replace "pom:project/pom:name" "<name>%{name}</name>"
%pom_xpath_replace "pom:project/pom:version" "<version>%{version}</version>"

# Fix jgoodies-forms artifactId
%pom_xpath_replace "pom:dependency[pom:groupId[./text()='com.jgoodies']][pom:artifactId[./text()='forms']]/pom:artifactId" "
	<artifactId>jgoodies-forms</artifactId>"

# Fix missing version warnings
%pom_xpath_inject "pom:project/pom:build/pom:plugins/pom:plugin[pom:artifactId[./text()='maven-compiler-plugin']]" "
	<version>any</version>"
%pom_xpath_inject "pom:project/pom:build/pom:plugins/pom:plugin[pom:artifactId[./text()='build-helper-maven-plugin']]" "
	<version>any</version>"
%pom_xpath_inject "pom:project/pom:build/pom:plugins/pom:plugin[pom:artifactId[./text()='maven-surefire-plugin']]" "
	<version>any</version>"

# Bundle
%pom_xpath_replace "pom:project/pom:packaging" "<packaging>bundle</packaging>" .

# Add an OSGi compilant MANIFEST.MF
%pom_add_plugin org.apache.felix:maven-bundle-plugin . "
<extensions>true</extensions>
<configuration>
	<supportedProjectTypes>
		<supportedProjectType>bundle</supportedProjectType>
		<supportedProjectType>jar</supportedProjectType>
	</supportedProjectTypes>
	<instructions>
		<Bundle-Name>\${project.artifactId}</Bundle-Name>
		<Bundle-Version>\${project.version}</Bundle-Version>
	</instructions>
</configuration>
<executions>
	<execution>
		<id>bundle-manifest</id>
		<phase>process-classes</phase>
		<goals>
			<goal>manifest</goal>
		</goals>
	</execution>
</executions>"

# Add the META-INF/INDEX.LIST (fix jar-not-indexed warning) and
# the META-INF/MANIFEST.MF to the jar archive
%pom_add_plugin :maven-jar-plugin . "
<executions>
	<execution>
		<phase>package</phase>
		<configuration>
			<archive>
				<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
				<manifest>
					<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
					<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
				</manifest>
				<index>true</index>
			</archive>
		</configuration>
		<goals>
			<goal>jar</goal>
		</goals>
	</execution>
</executions>"

# Fix jar name
%mvn_file :%{name} %{name}-%{version} %{name}

%build
%mvn_build

%install
%mvn_install

